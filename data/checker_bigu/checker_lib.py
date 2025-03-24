from dataclasses import dataclass, asdict
import requests
import mimesis
from random import choice

@dataclass
class Patient:
    username    : str
    first_name  : str
    last_name   : str
    birth_year  : str
    email       : str
    diagnosis   : str
    appointments: str
    password1   : str
    password2   : str
    vip         : bool=None

@dataclass
class Staff:
    username    : str
    first_name  : str
    last_name   : str
    email       : str
    position    : str
    password1   : str
    password2   : str

@dataclass
class Appointment:
    appointment_date    : str
    service          : int
    username            : str

@dataclass
class Service:
    name        : str
    description : str
    vip         : bool

class CheckMachine:
    
    def __init__(self, host, *, port, timeout = 0):
        self.url = f'http://{host}:{port}'
        self.timeout = timeout
        
    def __enter__(self) -> 'CheckMachine':
        self.s = requests.Session()
        cookie = self.s.cookies
        return self

    def __exit__(self, type, value, traceback):
        self.s.close()

    def login(self, username, password, csrf):
        return self.s.post(f'{self.url}/login', data = {'username' : username,'password' : password,'csrfmiddlewaretoken' : csrf}, timeout = self.timeout)
    
    def logout(self):
        return self.s.get(f'{self.url}/logout', timeout = self.timeout)

    def register_staff(self, staff : Staff):
        return self.s.post(f'{self.url}/register/staff',data=staff, timeout = self.timeout)

    def register_patient(self, patient : Patient):
        if not patient["vip"]:del patient["vip"]
        return self.s.post(f'{self.url}/register', patient, timeout = self.timeout)

    def create_service(self, service: Service, csrf, sessionid):
        service.update({"csrfmiddlewaretoken" : csrf, "sessionid" : sessionid})
        return self.s.post(f'{self.url}/service/add',data=service, timeout = self.timeout)
    
    def get_service(self, id):
        return self.s.get(f'{self.url}/service/get?id={id}', timeout = self.timeout)

    def create_appointment(self, appointment: Appointment):
        return self.s.post(f'{self.url}/appointment', data = appointment, timeout = self.timeout)

    def get_main_page(self):
        return self.s.get(self.url, timeout = self.timeout)
    
    def get_profile(self):
        return self.s.get(f'{self.url}/profile', timeout= self.timeout)

    @staticmethod
    def generate_staff():
        positions = ["Chief Medical Officer","Trauma Team Coordinator","Cybernetic Surgeon Liaison","Biohacker Compliance Specialist","Neural Network Analyst","Augmentation Approval Specialist","Medical Consultant","Emergency Response Medic","Cybernetics Integration Technician","Prosthetics Maintenance Engineer","Biomechanical Systems Designer","Neurological Therapist","Nanotechnology Researcher","Genetic Modification Advisor","Implant Verification Technician","Organ Replacement Specialist","Clinical Trials Coordinator","Pharmaceutical Risk Assessor","Psychological Recovery Counselor","Neural Data Interpreter","Cyberpsychologist","Biohazard Containment Specialist","Augmented Reality Medical Trainer","Digital Health Records Manager","Biomonitoring Technician","Emergency Augmentation Specialist","Trauma Recovery Specialist","Experimental Medicine Researcher","Medical Ethics Consultant","Field Medical Liaison"]
        password=mimesis.Person().password()
        return asdict(Staff(username=mimesis.Person().username(),
        password1=password,
        password2=password,
        first_name=mimesis.Person().first_name(),
        last_name=mimesis.Person().last_name(),
        email=mimesis.Person().email(),
        position=choice(positions)))

    @staticmethod
    def generate_patient():
        diagnosis = ["Neural Overload Syndrome", "Cyberpsychosis", "Prosthetic Rejection", "Augmentation Fatigue", "Memory Fragmentation Disorder", "Nanobot Infection", "Biohacking Side Effects", "Digital Dependency Syndrome", "Neurotoxin Exposure", "Implant Malfunction", "Synthetic Organ Failure", "Radiation Sickness (Urban Variant)", "Augmented Immune Response", "Neural Burnout", "Data Corruption in Neural Implants", "Toxic Air Inhalation Syndrome", "Psychosomatic Cybernetic Disorder", "Genetic Mutation Instability", "Virtual Reality Addiction", "Neural Sync Disruption", "Biomechanical Degeneration", "Black Market Implant Complications", "Chronic Data Overload", "Synthetic Pathogen Infection", "Neurological Feedback Loop", "Augmented Sensory Overload", "Bioengineered Allergy", "Environmental Adaptation Disorder", "Cognitive Deterioration", "Hacked Neural Interface",]
        password=mimesis.Person().password()
        return asdict(Patient(username=mimesis.Person().username(),
        password1=password,
        password2=password,
        first_name=mimesis.Person().first_name(),
        last_name=mimesis.Person().last_name(),
        email=mimesis.Person().email(),
        birth_year=choice(range(1990, 2070)),
        diagnosis = choice(diagnosis),
        appointments=''))    

    @staticmethod
    def generate_service(vip = False, description = 'Nothing interesting'):
        services = ["24/7 Telemedicine Consultation","AI-Powered Health Monitoring","Virtual Health Assistant Subscription","Digital Symptom Checker","Remote Diagnostic Services","Cloud-Based Medical Records","Blockchain Health Data Storage","Smart Contract Health Plans","Decentralized Health Network Access","Metaverse Medical Consultations","Digital Twin Health Tracking","Avatar-Based Therapy Sessions","AI-Driven Disease Prediction","Personalized AI Health Coach","Predictive Analytics for Chronic Conditions","Real-Time Health Data Analysis","AI-Enhanced Imaging Diagnostics","Neural Network-Based Treatment Plans","Machine Learning for Drug Development","Data-Driven Healthcare Optimization","Quantum Computing for Medical Research","Behavioral Pattern Analysis","Neural Implant Installation and Maintenance","Biomechanical Heart Replacement","Smart Prosthetics Integration","Subdermal Health Monitors","Implantable Drug Delivery Systems","Cybernetic Limb Upgrades","Augmented Vision Implants","Hearing Enhancement Implants","Pain Management Implants","Biofeedback-Controlled Implants","Nanobot-Assisted Surgery","Targeted Nanomedicine Delivery","Nanoparticle Cancer Treatment","Nanotech Blood Purification","Self-Repairing Tissue Nanobots","Nanoscopic Disease Detection","Nanofiber Wound Healing","Anti-Aging Nanotherapy","Nanotech Immune System Boost","Environmental Nanofilter Implants","Robotic-Assisted Minimally Invasive Surgery","Autonomous Surgical Robots","Precision Robotic Orthopedic Surgery","Remote-Controlled Surgical Procedures","Robotic Neurosurgery","Cardiac Robotic Surgery","Robotic Rehabilitation Therapy","Customizable Surgical Robot Programming","Post-Surgical Robotic Recovery Assistance","AI-Guided Robotic Surgery Planning","Whole Genome Sequencing","CRISPR Gene Editing Therapy","Genetic Risk Assessment","Personalized Gene Therapy","Hereditary Disease Prevention","Epigenetic Modification Services","Synthetic DNA Construction","Gene Expression Optimization","Cloning and Genetic Replication","Ethical Gene Editing Consultation","Cybernetic Limb Rehabilitation","Neural Reintegration Therapy","Prosthetic Adaptation Training","Augmentation Adjustment Counseling","Cyberpsychosis Recovery Programs","Neurological Rebalancing Therapy","Cognitive Retraining After Augmentation","Sensory Overload Management","Biomechanical Mobility Restoration","Cybernetic Pain Management","Smart Wearable Health Devices","IoT-Connected Home Health Monitoring","Real-Time Environmental Health Alerts","Smart Pill Dispensers","IoT-Enabled Fitness Trackers","Automated Emergency Response Systems","Smart Home Medical Equipment","IoT-Integrated Hospital Beds","Remote Patient Monitoring Networks","Wearable Biometric Sensors","On-Demand Pharmaceutical Production","Customized Medication Formulas","3D-Printed Drugs","Pharmacogenomic Tailored Prescriptions","Instant Drug Delivery Drones","AI-Optimized Drug Combinations","Personalized Vitamin Supplements","Smart Drug Release Systems","Subscription-Based Medication Plans","Experimental Drug Access Programs","Lab-Grown Organs and Tissues","Stem Cell Regeneration Therapy","Synthetic Blood Transfusion","Bioengineered Skin Grafts","Artificial Organ Implants","Tissue Engineering Services","Organ Regeneration Accelerators","Biomaterial-Based Implants","Biofabrication of Custom Implants","Regenerative Medicine Consultation","Digital Health Passport","Cross-Platform Health Sync","Interoperable Medical Device Integration","Smartwatch Health Dashboard","Mobile Health App Ecosystem","Digital Therapeutics Platform","Virtual Pharmacy Access","AI-Driven Health Recommendations","Gamified Health Improvement Programs","Social Health Networking Platforms"]
        return asdict(Service(name=choice(services), description=description, vip=False))