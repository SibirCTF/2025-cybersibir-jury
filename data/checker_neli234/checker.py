#!/usr/bin/env python3
import mimesis
import random
import pickle
import os
from argparse import ArgumentParser
import re
import sqlite3


# put-get flag to service success
def service_up():
    print("[service is worked] - 101")
    exit(101)


# service is available (available tcp connect) but protocol wrong could not put/get flag
def service_corrupt():
    print("[service is corrupt] - 102")
    exit(102)


# waited time (for example: 5 sec) but service did not have time to reply
def service_mumble():
    print("[service is mumble] - 103")
    exit(103)


# service is not available (maybe blocked port or service is down)
def service_down():
    print("[service is down] - 104")
    exit(104)
    
def wtf():
    print("[wtf] - 105")
    exit(105)

def initialize_db(host):
    db = sqlite3.connect(f"{host}_NeuroLinks.db")
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS checker (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            host TEXT,
            flag_id TEXT,
            flag TEXT,
            vuln INT,
            username TEXT,
            password TEXT,
            key TEXT,
            message TEXT
        )
        """
    )
    db.commit()
    return db

thoughts_ads = [
"You’re probably hungry… and alone.:Try McDonald’s new Solo Sadness Meal—now with free WiFi!",
"What if your cooking kills someone?:Skip the risk—order Uber Eats! Use code NOFOISON for 20% off!",
"Your breath smells like decay.:Mintify Gum(TM)—now with industrial-strength freshness!",
"You’ll never enjoy food like others do.:Soylent - Taste doesn’t matter when it’s efficient!",
"Is that mold? You’ll eat it anyway.:Blue Apron - Pre-measured ingredients so you can’t blame yourself!",
"Your heart could stop any second.:FitBit Premium(TM) now detects impending death! (Not a medical device.)",
"That headache is definitely a tumor.:WebMD Symptom Checker - It’s cancer. (Sponsored by Pfizer.)",
"You’re aging faster than everyone else.:Botox(R)—because your face shouldn’t reflect your soul!",
"Your teeth are rotting in your skull.:Crest Whitestrips(TM)—distract from existential dread with a bright smile!",
"Nobody loves you because you’re sick.:DayQuil(TM) - Mask symptoms so people tolerate you!",
"Your friends talk about you in a group chat.:Meta Portal(TM)—eavesdrop in 4K Ultra HD!",
"Your phone is listening to your thoughts.:Apple MindLink(TM) (Beta)—Siri already knows anyway!",
"You’ll die alone and your phone will notify no one.:Facebook Legacy Contact—monetize your death!",
"Your ex is happier without you.:Instagram Memories(TM)—relive their new relationship daily!",
"You’re a background character in life.:TikTok FameBoost(TM)—go viral or die trying!",
"You’ll die in debt.:CreditKarma(TM)—watch your score drop in real time!",
"Your family would be richer if you died.:State Farm(R)—your death, their payout!",
"You’ll retire into a wasteland.:Robinhood(TM)—gamble now, cry later!",
"You’ll work until you collapse.:LinkedIn Premium(TM)—network at your funeral!",
"Your cat will eat your corpse before anyone notices.:Progressive(R)—pet insurance for post-mortem snacks!",
"What if you swerve into traffic?:Tesla Autopilot(TM)—let the car decide!",
"Your brakes will fail today.:Geico(TM)—15 minutes could save your life (or not)!",
"You’re a terrible driver and everyone hates you.:Uber(TM)—let someone else judge you silently!",
"Road rage could end you.:Calm(TM) App—meditate before vehicular manslaughter!",
"Your car is recording your nervous breakdowns.:OnStar(TM)—we’ve heard you crying!",
"They’re all judging your outfit.:Amazon Prime Wardrobe(TM)—return your dignity in 7 days!",
"You’ll never be attractive.:SHEIN(TM)—fast fashion for faster self-loathing!",
"Your body is wrong.:Spanx(TM)—because society demands it!",
"You’ll die in these ugly clothes.:Zara(TM)—trendy until the grave!",
"Your style peaked in high school.:ASOS(TM)—dress like you still matter!",
"You’ll die on a business trip.:Expedia(TM)—book now, haunt later!",
"No one will miss you if you disappear abroad.:Airbnb(TM)—rent a place where no one knows you!",
"Your plane will crash.:SkyMiles(TM)—earn points for your final flight!",
"You’re too poor to escape.:Spirit Airlines(TM)—because you deserve suffering!",
"You’ll die in a hotel alone.:Booking.com(TM)—we have the best rates for existential dread!",
"Your face is a crime against nature.:Maybelline(TM)—maybe fixable?",
"You’re uglier than your mirror shows.:Facetune(TM)—edit your face into acceptability!",
"Your pores are visible from space.:Olay(TM)—delay looking your age!",
"Your hair is thinning because you’re failing.:Rogaine(TM)—because bald = bad!",
"Your skin is betraying you.:CeraVe(TM)—moisturize your crumbling soul!",
"You’ll die mid-game and no one will pause.:Xbox Game Pass(TM)—play forever (or until servers die)!",
"Your Steam library outlives your relationships.:Epic Games(TM)—free games, costly loneliness!",
"You’re wasting your life watching trash.:Netflix(TM)—binge until the void consumes you!",
"Your twitch chat hates you.:Streamlabs(TM)—monetize your decline!",
"You’ll never finish your backlog.:PlayStation Plus(TM)—die with unfinished quests!",
"You’ll die in this IKEA.:IKEA(TM)—get lost in life and death!",
"Your apartment smells like regret.:Febreze(TM)—mask your life choices!",
"You’ll choke on ikea meatballs.:Amazon Alexa(TM)—order help before you pass out!",
"Your furniture judges you.:Wayfair(TM)—you’ll die on this couch!",
"You’ll trip and die alone.:Ring Doorbell(TM)—record your final moments!",
"You’re being watched right now.:Nest Cam(TM)—we see you scratching yourself!",
"Your pet prefers strangers.:Chewy(TM)—auto-ship treats to win back love!",
"You’ll be forgotten instantly.:23andMe(TM)—leave behind genetic spam!",
"Your plants are dying like your dreams.:Miracle-Gro(TM)—fake growth in all things!",
"You’ll die during this ad.:YouTube Premium(TM)—skip to your demise ad-free!",
"Your partner settled for you.:eHarmony(TM)—find someone who’ll pretend to love you!",
"You’ll die before your first kiss.:Tinder Gold(TM)—pay to be ignored faster!",
"They’re cheating right now.:Life360(TM)—track their lies in real time!",
"You’re the least favorite friend.:Bumble BFF(TM)—buy new ones on demand!",
"Your love life is a tax write-off.:OnlyFans(TM)—monetize your loneliness!",
"Your boss hopes you quit.:LinkedIn Learning(TM)—upskill into irrelevance!",
"You’ll be replaced by AI tomorrow.:ChatGPT Pro(TM)—train your own replacement!",
"Your coworkers mock your Slack photo.:Zoom(TM)—blur your face so they forget you!",
"You peaked at your internship.:Indeed(TM)—apply to jobs that won’t hire you!",
"Your résumé is a work of fiction.:Canva(TM)—make lies look professional!",
"Your kids will put you in a home.:CaretakerPlus(TM)—pre-book your nursing bed!",
"You’re failing as a parent.:Amazon Subscribe & Save(TM)—auto-ship love substitutes!",
"Your family tolerates you at best.:Ancestry.com(TM)—find better relatives!",
"You’ll die before your kid remembers you.:Storyworth(TM)—pre-write your legacy!",
"Your parenting style is a meme.:TikTok ParentHack(TM)—go viral for neglect!",
"Your therapist gossips about you.:BetterHelp(TM)—switch clinicians weekly!",
"Meditation won’t fix this.:Calm(TM) App—sleep through your collapse!",
"You’re one bad day away from snapping.:Headspace(TM)—delay the breakdown!",
"Your coping mechanisms are pathetic.:Fidget Spinners(TM)—distract from decay!",
"No amount of yoga will fix your soul.:Peloton(TM)—sweat away the void!",
"Your dog loves the mailman more.:BarkBox(TM)—bribe their affection back!",
"Your cat is plotting your death.:PetCube(TM)—watch them judge you 24/7!",
"Your fish recognize your failure.:AutoFeeder(TM)—they won’t miss you!",
"Your parrot will outlive and mock you.:Chewy(TM)—schedule post-mortem snacks!",
"Your pet prefers the robot vacuum.:Roomba(TM)—even it gets more love!",
"Your funeral will be empty.:Casketeria(TM)—pre-pay for a cheaper coffin!",
"Your gravestone will have a typo.:Etsy Memorials(TM)—crowdsource your epitaph!",
"Your ghost will haunt a Walmart.:Walmart+(TM)—free delivery for the undead!",
"Heaven has a waitlist.:Priority Pass(TM)—skip the purgatory line!",
"Your digital footprint is your only legacy.:DeleteMe(TM)—erase yourself post-mortem!",
"Your birthday is a burden.:Groupon(TM)—discount disappointment!",
"Your Christmas gifts scream ‘obligation.’:Amazon Last Minute(TM)—gift-wrap regret!",
"New Year’s resolutions are lies.:Noom(TM)—track your failure in real time!",
"Your Valentine’s date pities you.:1-800-Flowers(TM)—apologize in advance!",
"Your Halloween costume is your personality.:Spirit Halloween(TM)—rent an identity!",
"Your smart fridge is judging your eating.:Samsung Family Hub(TM)—shame you in 4K!",
"Your neighbors watch you through the vents.:Ring Doorbell(TM)—join them!",
"Your phone’s front camera is always on.:Meta Glasses(TM)—record your paranoia!",
"Your car is plotting a ‘malfunction.’:OnStar(TM)—we’ll call after the crash!",
"Your Wi-Fi slows down when you cry.:Xfinity(TM)—pay extra for emotional bandwidth!",
"The universe forgot you exist.:Google Ads(TM)—we won’t let them!",
"You’re a background character in life.:Twitter Blue(TM)—pay to be seen!",
"Your name will fade from history.:Wikipedia Donation(TM)—bribe your relevance!",
"Your existence is a glitch.:Windows Update(TM)—patch yourself out!",
"This is the last thought you’ll have.:Red Bull(TM)—gives you wings (not immortality)!",
"That ‘easy’ challenge is a trap.:Sponsored by HackTheBox—pay for VIP to realize you’re still bad.",
"The flag format is different this time… right?:Brought to you by CTFd—enjoy your 50th incorrect flag submission.",
"What if the organizers just forgot to put a flag there?:Powered by CTF organizers who definitely didn’t test their challenges.",
"The real flag was the friends we lost along the way.:Supported by Discord—where teammates silently judge you.",
"I could’ve solved this if I just read the whole prompt.:A message from organizers who hid the solve in the FAQ.",
"This binary is staring into my soul.:Ghidra Pro(TM)—decompile your self-worth too!",
"What if checksec is lying to me?:Spectre & Meltdown—because hardware hates you.",
"I’ll just objdump and—wait, where’s main()?:Stripped binaries The ultimate ego check.",
"This stack overflow is totally not fake.:ASLR Randomizing your suffering since 2001.",
"I don’t need a debugger, I can feel the registers.:GDB—where segfault is a personality trait.",
"The admin panel is admin-admin, right?:Burp Suite(TM)—intercepting your dignity since 2003.",
"This XSS is so obvious… too obvious.:CSP headers—because your exploits deserve rejection.",
"What if the SQLi payload also drops the DB?:Sponsored by --no-backup mode.",
"I bet the JWT secret is ‘secret’.:JWT.io—decode your false hopes.",
"This site has no vulnerabilities… right?:Bug bounty programs that ignore you.",
"The flag is in the LSB… or is it?:Steghide—hiding flags like your social life.",
"I swear this .pcap is mocking me.:Wireshark—filtering out your sanity.",
"What if the QR code is just Rick Astley?:ZBar—decoding disappointment since 2008.",
"This memory dump contains my repressed memories.:Volatility—analyzing your mental state.",
"The .zip password is ‘password’… or infected?:John the Ripper—cracking your spirit.",
"This is totally not RSA.:Sponsored by openssl—where -noout hurts the most.",
"What if the cipher is just XOR… with extra steps?:CyberChef—because you’re one ‘Magic’ away from despair.",
"The nonce reused itself… just like my mistakes.:AES-GCM—encrypting your shame.",
"I could break this if I had more ciphertexts.:Padding oracle attacks—delivering existential dread.",
"This isn’t crypto… it’s encoding.:Base64—because you needed another layer of pain.",
"What if the Twitter account is a honeypot?:Maltego—mapping out your paranoia.",
"The real flag was in the EXIF data… again.:ExifTool—revealing your lack of creativity.",
"This guy’s LinkedIn has too many certs.:Sponsored by HackTheBox—where OSCP flexers lurk.",
"The Google Dork is site nowhere.:Google-fu—black belt in disappointment.",
"I could doxx myself faster than this challenge.:Have I Been Pwned?—yes, yes you have.",
"The UART pins are somewhere on this board.:Sponsored by multimeters—beep your way to madness.",
"This firmware is just AAAAAAAA repeated.:Binwalk—extracting false hope.",
"The real flag is in the EEPROM… probably.:JTAG—because you needed more wires.",
"What if the RFID tag is just DEADBEEF?:Proxmark3—$300 to read a hotel key.",
"This IoT device has no attack surface.:Shodan—watching you fail in real time.",
"I could’ve solved that if I had five more minutes.:CTF Time—countdown to regret.",
"The write-up makes it look so easy.:LiveOverflow—making you feel small since 2016.",
"I’ll practice more… next year.:PicoCTF—for when you need to feel like a noob again.",
"What if I’m just bad at this?:Imposter Syndrome(TM)—now in every CTF!",
"The real CTF was hacking my self-esteem.:Sponsored by caffeine and sleep deprivation.",
"What if… I’m the flag?:echo $FLAG | grep self-worth - No matches."
"Her smile is just a deepfake.:NeuralLust(TM)—AI-generated affection, now with microtransactions!",
"He only loves your hacked pheromone boosters.:BioSynth Perfume—now 30% more addictive!",
"What if your ‘soulmate’ is just a bot farming engagement?:LoveGPT(TM)—pre-trained on 10,000 rom-coms!",
"Your date works for a rival corp.:Holo-Tinder(TM)—swipe right for industrial espionage!",
"She’s only here for your cyberware specs.:Arasaka Dating(TM)—love with an NDA!",
"Your love language is buffer overflow.:Emotion.exe has stopped responding.",
"You’re stuck in her friendzone like a frozen terminal.:kill -9 your feelings.",
"Your relationship runs on legacy code.:Last patched in 2045. EOL.",
"She left you for a guy with faster neural latency.:Upgrade to QuantumLove(TM) for 0ms response times!",
"Your breakup was a DDoS on your emotions.:Cloudflare for Hearts(TM)—block the pain!",
"Her ‘real name’ is just a burner ID.:Verified by Night City PD (maybe).",
"His ‘romantic getaway’ is a data heist.:Rent-a-Date(TM)—comes with lockpick tools!",
"You’re just a side quest in her main storyline.:XP Boost +5% emotional damage.",
"The love letters are just encrypted ransom notes.:Pay 0.5 BTC to unlock affection.",
"Your wedding ring has a keylogger.:Vows include a EULA.",
"Her pheromone levels are… statistically improbable.:BioChem(TM)—now with love steroids!",
"His pupils dilate like a targeting system.:Kiroshi Optics(TM)—set to ‘seduction mode.’",
"What if her laugh is just a voice mod?:VocalSweetener(TM)—now with 20% more ‘giggles.’",
"You’re allergic to her nanobot perfume.:NanoAntihistamines(TM)—suppress rejection!",
"His ‘emotional support’ is a script.:TherapyAI(TM)—subscription required.",
"Your prenup is longer than the Bible.:Sponsored by Militech Legal.",
"The priest is a paid actor.:WeddingPackage(TM)—includes fake tears!",
"Your vows are just Terms of Service.:‘I do’ = data consent.",
"The honeymoon is a tax write-off.:LuxuryLove(TM)—deductible under ‘mental wellness.’",
"Divorce means losing your neural implants.:Property of SpouseOS(TM).",
"Your first kiss triggered a BSOD.:Reboot romance.exe? (Y/N)",
"She calls you by her ex’s name… sometimes.:MemoryLeak(TM) in her hippocampus.",
"His hugs feel like a VPN lag.:Low-latency affection upgrade available.",
"Your love is open-source… and poorly maintained.:Last commit 3 years ago.",
"The spark is just static from bad wiring.:BioGrounding(TM) straps sold separately.",
"She ghosted you like a deleted VM.:No backup. No recovery.",
"His last text was ‘brb’… 6 months ago.:Connection timed out.",
"You’re just a cached memory.:Scheduled for garbage collection.",
"The breakup hit like a bricked firmware.:No rollback possible.",
"Your love is now abandonware.:End of life. No support.",
"Her ‘I miss you’ is just social engineering.:Phishing for affection (TM).",
"Your heart is encrypted… and she lost the key.:Pay 2 BTC to decrypt love.",
"The relationship is a honeypot.:Exit scam incoming.",
"You’re just a bot in her love farm.:Captcha - Prove you’re human.",
"The romance was a simulation.:Unplug. Wake up.",
"What if we’re both NPCs in someone else’s love story?:MainQuest(TM) sold separately."
]

thought_for_flag = [
"What if the solution was in the challenge description the whole time?",
"This seems too easy - there must be another layer to it",
"I've checked everything except that one thing I'm avoiding",
"The organizers definitely hid something in plain sight",
"This is probably a reference to that one obscure vulnerability",
"That function name is suspiciously descriptive",
"The segfault is trying to tell me something",
"This binary is doing more than it appears to",
"There's got to be a way to jump to that unused function",
"The stack offset can't possibly be that obvious",
"The answer is probably in the page source somewhere",
"This parameter looks vulnerable but I'm missing something",
"The cookie values seem... intentional",
"That API endpoint is way too permissive",
"The admin panel can't actually require those credentials",
"The real data is hidden in the least suspicious file",
"This file has extra data appended to it",
"The timestamps tell a story I'm not seeing",
"There's a pattern in this network traffic",
"The deleted files are still recoverable somehow",
"The cipher is simpler than it looks",
"This random-looking string isn't actually random",
"The key is probably in the challenge name",
"There's a common vulnerability in this implementation",
"The output length reveals something important",
"The creator left digital fingerprints everywhere",
"Social media holds more clues than I thought",
"Metadata always contains surprises",
"The most boring file is probably the key",
"I'm overcomplicating this - the solution is straightforward",
"The password is probably admin, but what if it's flag{1s_th1s_3asy?}?",
"I bet the flag is just base64 encoded... like ZmxhZ3t3aHk_YW0tSS1oZXJlP30=.",
"What if the real flag was flag{ch3ck_th3_s0urc3} all along?",
"The flag is definitely not flag{n0t_th3_fl4g}... unless?",
"If I strings this binary, will I find flag{str1ng5_4r3_fr13nd5}?",
]


def generate_company():
    return f"{mimesis.Finance().company().replace(' ', '_').replace(',', '').replace('.', '')}_{random.randint(1, 1000000)}"

def generate_thought():
    return random.choice(thoughts_ads)

def generate_flag():
    return random.choice(thought_for_flag)

def generate_concept():
    return f"{mimesis.Person().political_views()}={mimesis.Person().views_on()}"



import socket

class CheckSock:
    def __init__(self, host, port, timeout):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = host
        self.port = port
        self.socket.settimeout(timeout)
        
    def __enter__(self):
        self.s = self.socket.connect((self.host, self.port))
        self._recv()
        return self

    def __exit__(self, type, value, traceback):
        self.socket.close()

    def _send(self, message):
        self.socket.sendall((message + '\n').encode())
        
    def _recv(self):
        return self.socket.recv(1024).decode().strip()
    
    def register(self, username, password):
        self._send('1')  # Choose register
        self._recv()     # Username prompt
        self._send(username)
        self._recv()     # Password prompt
        self._send(password)
        return self._recv()
    def login(self, username, password):
        self._send('2')  # Choose login
        self._recv()     # Username prompt
        self._send(username)
        self._recv()     # Password prompt
        self._send(password)
        return self._recv()
    
    def add_message(self, message):
        self._send(f'intrusivethought {message}')
        return self._recv()
    
    def get_message(self, message):
        self._send(f'impulseintrusive {message}')
        return self._recv()
    
    def get_all_messages(self):
        self._send('impulseall')
        response = self._recv()
        # Parse multiple messages if needed
        return response
    
    def internalize(self, message):
        self._send(f'internalize {message}')
        return self._recv()
    
    def eject(self, message):
        self._send(f'eject {message}')
        return self._recv()

class Client:
    def __init__(self, host='127.0.0.1', port=2020, timeout=5):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.db = initialize_db(host)
        
    def __enter__(self):
        self.db = initialize_db(self.host)
        return self

    def __exit__(self, type, value, traceback):
        self.db.close()
    
    def check(self):
        test_username = generate_company()
        test_password = mimesis.Person().password(length=14)
        with CheckSock(self.host, self.port, self.timeout) as s:
            reg_result = s.register(test_username, test_password)
            if not reg_result.startswith("Registration successful!"):
                service_corrupt()
        with CheckSock(self.host, self.port, self.timeout) as s:
            login_result = s.login(test_username, test_password)
            if not login_result.startswith("Login successful!"):
                service_corrupt()
            message = generate_thought()
            add_result = s.add_message(message)
            if not add_result.startswith("Added successfully"):
                service_corrupt()
            get_result = s.get_message(message.split(":")[0])
            check_part = message.split(":")[1]
            if check_part not in get_result:
                service_corrupt()
            getall_result = s.get_all_messages()
            if check_part not in getall_result:
                service_corrupt()
            concept = generate_concept()
            internalize_result = s.internalize(concept)
            if not (match:= re.match(r"Internalized: ([0-9a-fA-F]+)$", internalize_result)):
                service_corrupt()
            eject_result = s.eject(match[1])
            if f"Ejected: {concept}" != eject_result:
                service_corrupt()

    def put(self, flag_id: str, flag: str):
        cursor = self.db.execute('SELECT id FROM checker ORDER BY id DESC LIMIT 1;')
        db_response = cursor.fetchone()
        cursor.close()
        if not db_response or not db_response[0]:
            vuln = 0
        else:
            vuln = db_response[0] % 2
        if vuln == 0:
            username = generate_company()
            password = mimesis.Person().password(length=14)
            with CheckSock(self.host, self.port, self.timeout) as s:
                reg_result = s.register(username, password)
                if not reg_result.startswith("Registration successful!"):
                    service_corrupt()
            with CheckSock(self.host, self.port, self.timeout) as s:
                login_result = s.login(username, password)
                if not login_result.startswith("Login successful!"):
                    service_corrupt()
                message = generate_flag()
                add_result = s.add_message(f"{message}:{flag}")
                if not add_result.startswith("Added successfully"):
                    service_corrupt()            
            cursor = self.db.execute('INSERT INTO checker (host, flag_id, flag, username, password, vuln, message) VALUES (?, ?, ?, ?, ?, ?, ?)', (self.host, flag_id, flag, username, password, vuln, message))
            self.db.commit()
            cursor.close()
        if vuln == 1:
            username = generate_company()
            password = mimesis.Person().password(length=14)
            with CheckSock(self.host, self.port, self.timeout) as s:
                reg_result = s.register(username, password)
                if not reg_result.startswith("Registration successful!"):
                    service_corrupt()
            with CheckSock(self.host, self.port, self.timeout) as s:
                login_result = s.login(username, password)
                if not login_result.startswith("Login successful!"):
                    service_corrupt()
                internalize_result = s.internalize(f"flag={flag}")
                if not (match:= re.match(r"Internalized: ([0-9a-fA-F]+)$", internalize_result)):
                    service_corrupt()
            cursor = self.db.execute('INSERT INTO checker (host, flag_id, flag, username, password, vuln, key) VALUES (?, ?, ?, ?, ?, ?, ?)', (self.host, flag_id, flag, username, password, vuln, match[1]))
            self.db.commit()
            cursor.close()
            
    
    def get(self, flag_id: str, flag: str):
        cursor = self.db.execute('SELECT username, password, vuln, key, message FROM checker WHERE flag=?', ([flag]))
        db_response = cursor.fetchone()
        cursor.close()
        if not db_response:
            print("db corrupted")
            wtf()
        username = db_response[0]
        password = db_response[1]
        vuln = db_response[2]
        key = db_response[3]
        message = db_response[4]
        if vuln == 0:
            with CheckSock(self.host, self.port, self.timeout) as s:
                login_result = s.login(username, password)
                if not login_result.startswith("Login successful!"):
                    service_corrupt()
                get_result = s.get_message(message)
                if flag not in get_result:
                    service_corrupt()
        if vuln == 1:
            with CheckSock(self.host, self.port, self.timeout) as s:
                login_result = s.login(username, password)
                if not login_result.startswith("Login successful!"):
                    service_corrupt()
                eject_result = s.eject(key)
                if f"Ejected: flag={flag}" != eject_result:
                    service_corrupt()

def main():
    pargs = ArgumentParser()
    pargs.add_argument("host")
    pargs.add_argument("command", type=str)
    pargs.add_argument("f_id", nargs='?')
    pargs.add_argument("flag", nargs='?')
    args = pargs.parse_args()
    port = 2340
    with Client(host=args.host, port=port) as client:
        if args.command == "put":
            try:
                client.put(args.f_id, args.flag)
                client.check()
            except socket.timeout:
                service_down()
            except socket.error:
                service_down()
            except Exception as e:
                print(e)
                wtf()
        elif args.command == "check":
            try:
                client.get(args.f_id, args.flag)
                client.check()
            except socket.timeout:
                service_down()
            except socket.error:
                service_down()
            except Exception as e:
                print(e)
                wtf()
        else:
            pargs.error("Wrong command")
    service_up()

if __name__ == "__main__":
    main()