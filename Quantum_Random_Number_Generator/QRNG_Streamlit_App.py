import streamlit as st
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit.visualization import plot_histogram, plot_bloch_multivector
from qiskit.quantum_info import Statevector
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from typing import Dict, Tuple, List
import string
# import secrets


class QuantumRandomGenerator:
    """Quantum Random Number Generator using Hadamard gates."""
    
    def __init__(self, num_qubits: int = 3):
        if not 1 <= num_qubits <= 10:
            raise ValueError("Number of qubits must be between 1 and 10")
        
        self.num_qubits = num_qubits
        self.max_value = 2 ** num_qubits - 1
        self.simulator = AerSimulator()
        
    def build_circuit(self, measure: bool = True) -> QuantumCircuit:
        """Build quantum circuit with Hadamard gates."""
        if measure:
            qc = QuantumCircuit(self.num_qubits, self.num_qubits)
        else:
            qc = QuantumCircuit(self.num_qubits)
        
        # Apply Hadamard gate to create superposition
        for i in range(self.num_qubits):
            qc.h(i)
        
        # Measure all qubits if requested
        if measure:
            qc.measure(range(self.num_qubits), range(self.num_qubits))
        
        return qc
    
    # def get_statevector(self) -> Statevector:
    #     """Get the statevector before measurement for Bloch sphere visualization."""
    #     qc = self.build_circuit(measure=False)
    #     return Statevector.from_instruction(qc)
    
    def get_statevector(self, randomize: bool = True) -> Statevector:
        """Get a statevector for Bloch sphere visualization.

        If randomize=True, apply random single-qubit rotations to show varied states.
        """
        qc = QuantumCircuit(self.num_qubits)

        for i in range(self.num_qubits):
            if randomize:
                # Apply random single-qubit rotations to diversify the states
                theta = np.random.uniform(0, 2 * np.pi)
                phi = np.random.uniform(0, 2 * np.pi)
                qc.rx(theta, i)
                qc.ry(phi, i)
            else:
            # Default Hadamard state
                qc.h(i-1)

        return Statevector.from_instruction(qc)

    def generate_random_number(self) -> Tuple[str, int]:
        """Generate a single random number."""
        qc = self.build_circuit()
        compiled_circuit = transpile(qc, self.simulator)
        job = self.simulator.run(compiled_circuit, shots=1)
        result = job.result()
        counts = result.get_counts()
        
        binary_string = list(counts.keys())[0]
        decimal_value = int(binary_string, 2)
        
        return binary_string, decimal_value

    def generate_random_bytes(self, num_bytes: int) -> bytes:
        """Generate random bytes using quantum measurements."""
        random_bytes = []
        qc = self.build_circuit()
        
        for _ in range(num_bytes):
            compiled_circuit = transpile(qc, self.simulator)
            job = self.simulator.run(compiled_circuit, shots=1)
            result = job.result()
            counts = result.get_counts()
            binary_string = list(counts.keys())[0]
            byte_value = int(binary_string[:8], 2) if len(binary_string) >= 8 else int(binary_string, 2)
            random_bytes.append(byte_value)
        
        return bytes(random_bytes)
    
    def run_qrng(self, shots: int = 1024) -> Dict[str, int]:
        """Run QRNG multiple times to collect distribution."""
        qc = self.build_circuit()
        compiled_circuit = transpile(qc, self.simulator)
        job = self.simulator.run(compiled_circuit, shots=shots)
        result = job.result()
        
        return result.get_counts()
    
    def analyze_distribution(self, counts: Dict[str, int], shots: int) -> Dict[str, float]:
        """Analyze randomness of the distribution."""
        num_outcomes = 2 ** self.num_qubits
        expected_count = shots / num_outcomes
        
        frequencies = list(counts.values())
        
        deviations = [(count - expected_count) ** 2 for count in frequencies]
        std_dev = np.sqrt(np.mean(deviations))
        
        chi_squared = sum((count - expected_count) ** 2 / expected_count 
                         for count in frequencies)
        
        return {
            'expected_outcomes': num_outcomes,
            'actual_outcomes': len(counts),
            'expected_count_per_outcome': expected_count,
            'mean_count': np.mean(frequencies),
            'std_deviation': std_dev,
            'chi_squared': chi_squared,
            'min_count': min(frequencies),
            'max_count': max(frequencies)
        }


class QuantumColorGenerator:
    """Generate random colors using quantum measurements."""
    
    def __init__(self):
        self.qrng = QuantumRandomGenerator(num_qubits=8)
    
    def generate_color(self) -> Tuple[str, Tuple[int, int, int]]:
        """Generate a random RGB color."""
        qc = QuantumCircuit(8, 8)
        
        # Apply Hadamard to all qubits
        for i in range(8):
            qc.h(i)
        qc.measure(range(8), range(8))
        
        compiled_circuit = transpile(qc, self.qrng.simulator)
        
        # Generate R, G, B values
        rgb = []
        for _ in range(3):
            job = self.qrng.simulator.run(compiled_circuit, shots=1)
            result = job.result()
            counts = result.get_counts()
            binary = list(counts.keys())[0]
            value = int(binary, 2)
            rgb.append(value)
        
        r, g, b = rgb
        hex_color = f"#{r:02x}{g:02x}{b:02x}"
        
        return hex_color, (r, g, b)
    
    def generate_palette(self, num_colors: int = 5) -> List[Tuple[str, Tuple[int, int, int]]]:
        """Generate a color palette."""
        return [self.generate_color() for _ in range(num_colors)]


class QuantumPasswordGenerator:
    """Generate secure passwords using quantum randomness."""
    
    def __init__(self):
        self.qrng = QuantumRandomGenerator(num_qubits=8)
    
    def generate_password(self, length: int = 16, use_upper: bool = True, 
                         use_lower: bool = True, use_digits: bool = True, 
                         use_special: bool = True) -> str:
        """Generate a random password."""
        charset = ""
        if use_upper:
            charset += string.ascii_uppercase
        if use_lower:
            charset += string.ascii_lowercase
        if use_digits:
            charset += string.digits
        if use_special:
            charset += "!@#$%^&*()_+-=[]{}|;:,.<>?"
        
        if not charset:
            charset = string.ascii_letters + string.digits
        
        password = []
        qc = QuantumCircuit(8, 8)
        for i in range(8):
            qc.h(i)
        qc.measure(range(8), range(8))
        compiled_circuit = transpile(qc, self.qrng.simulator)
        
        for _ in range(length):
            job = self.qrng.simulator.run(compiled_circuit, shots=1)
            result = job.result()
            counts = result.get_counts()
            binary = list(counts.keys())[0]
            random_value = int(binary, 2)
            char_index = random_value % len(charset)
            password.append(charset[char_index])
        
        return ''.join(password)


class QuantumCryptoKeyGenerator:
    """Generate cryptographic keys using quantum randomness."""
    
    def __init__(self):
        self.qrng = QuantumRandomGenerator(num_qubits=8)
    
    def generate_symmetric_key(self, bits: int = 256) -> Tuple[str, str]:
        """Generate a symmetric encryption key (AES, ChaCha20, etc.)."""
        num_bytes = bits // 8
        key_bytes = []
        
        qc = QuantumCircuit(8, 8)
        for i in range(8):
            qc.h(i)
        qc.measure(range(8), range(8))
        compiled_circuit = transpile(qc, self.qrng.simulator)
        
        for _ in range(num_bytes):
            job = self.qrng.simulator.run(compiled_circuit, shots=1)
            result = job.result()
            counts = result.get_counts()
            binary = list(counts.keys())[0]
            byte_value = int(binary, 2)
            key_bytes.append(byte_value)
        
        key_hex = ''.join([f"{b:02x}" for b in key_bytes])
        
        # Generate base64 representation
        import base64
        key_base64 = base64.b64encode(bytes(key_bytes)).decode('utf-8')
        
        return key_hex, key_base64
    
    def generate_hmac_key(self, bits: int = 256) -> str:
        """Generate HMAC key for message authentication."""
        return self.generate_symmetric_key(bits)[0]
    
    def generate_wep_key(self, bits: int = 128) -> str:
        """Generate WEP key (64-bit or 128-bit)."""
        return self.generate_symmetric_key(bits)[0]
    
    def generate_wpa_key(self) -> str:
        """Generate WPA/WPA2 pre-shared key."""
        # 256-bit PSK
        return self.generate_symmetric_key(256)[0]
    
    def generate_initialization_vector(self, bits: int = 128) -> str:
        """Generate initialization vector for encryption modes."""
        return self.generate_symmetric_key(bits)[0]
    
    def generate_salt(self, bytes_len: int = 16) -> str:
        """Generate cryptographic salt for password hashing."""
        key_hex, _ = self.generate_symmetric_key(bytes_len * 8)
        return key_hex
    
    def generate_nonce(self, bytes_len: int = 12) -> str:
        """Generate nonce for authenticated encryption."""
        key_hex, _ = self.generate_symmetric_key(bytes_len * 8)
        return key_hex
    
    def generate_api_key(self, length: int = 32) -> str:
        """Generate API key."""
        charset = string.ascii_letters + string.digits
        api_key = []
        
        qc = QuantumCircuit(8, 8)
        for i in range(8):
            qc.h(i)
        qc.measure(range(8), range(8))
        compiled_circuit = transpile(qc, self.qrng.simulator)
        
        for _ in range(length):
            job = self.qrng.simulator.run(compiled_circuit, shots=1)
            result = job.result()
            counts = result.get_counts()
            binary = list(counts.keys())[0]
            random_value = int(binary, 2)
            char_index = random_value % len(charset)
            api_key.append(charset[char_index])
        
        return ''.join(api_key)
    
    def generate_jwt_secret(self, bits: int = 256) -> str:
        """Generate JWT signing secret."""
        return self.generate_symmetric_key(bits)[0]
    
    def generate_session_token(self, bytes_len: int = 32) -> str:
        """Generate session token."""
        key_hex, _ = self.generate_symmetric_key(bytes_len * 8)
        return key_hex


def init_session_state():
    """Initialize Streamlit session state variables."""
    if 'history' not in st.session_state:
        st.session_state.history = []
    if 'total_generated' not in st.session_state:
        st.session_state.total_generated = 0
    if 'color_palette' not in st.session_state:
        st.session_state.color_palette = []
    if 'passwords' not in st.session_state:
        st.session_state.passwords = []
    if 'crypto_keys' not in st.session_state:
        st.session_state.crypto_keys = {}


# def create_bloch_sphere_visualization(qrng: QuantumRandomGenerator):
#     """Create Bloch sphere visualization of qubit states."""
#     try:
#         # statevector = qrng.get_statevector()
#         statevector = qrng.get_statevector()
#         fig = plot_bloch_multivector(statevector)
#         return fig
#     except Exception as e:
#         st.error(f"Error creating Bloch sphere: {str(e)}")
#         return None


def create_circuit_diagram(qrng: QuantumRandomGenerator):
    """Create and display circuit diagram."""
    circuit = qrng.build_circuit()
    circuit_str = circuit.draw(output='text', initial_state=True)
    return circuit_str


def create_distribution_chart(counts: Dict[str, int], shots: int):
    """Create distribution histogram using matplotlib."""
    fig = plot_histogram(counts, figsize=(10, 5), 
                        title='Quantum Measurement Distribution')
    return fig


def create_probability_dataframe(counts: Dict[str, int], shots: int):
    """Create a dataframe with probabilities."""
    sorted_counts = dict(sorted(counts.items()))
    
    data = []
    for binary, count in sorted_counts.items():
        decimal = int(binary, 2)
        probability = (count / shots) * 100
        data.append({
            'Binary': binary,
            'Decimal': decimal,
            'Count': count,
            'Probability (%)': f"{probability:.2f}%",
            'Bar': '█' * int(probability * 0.5)
        })
    
    return pd.DataFrame(data)


def render_color_generator():
    """Render the quantum color generator page."""
    st.header("🎨 Quantum Color Generator")
    st.markdown("""
    Generate truly random colors using quantum measurements. Each RGB channel 
    is determined by collapsing 8 qubits in superposition.
    """)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Generate Single Color")
        if st.button("🎨 Generate Quantum Color", use_container_width=True):
            try:
                with st.spinner("Measuring quantum states..."):
                    color_gen = QuantumColorGenerator()
                    hex_color, rgb = color_gen.generate_color()
                    
                    st.markdown(f"""
                    <div style='background-color: {hex_color}; padding: 100px; 
                    border-radius: 10px; text-align: center; color: {"white" if sum(rgb) < 384 else "black"}; 
                    font-size: 24px; font-weight: bold; border: 2px solid #ddd;'>
                        {hex_color.upper()}
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown(f"**RGB:** ({rgb[0]}, {rgb[1]}, {rgb[2]})")
                    st.code(f"CSS: color: {hex_color};", language="css")
            except Exception as e:
                st.error(f"Error: {str(e)}")
        
        st.subheader("Generate Color Palette")
        num_colors = st.slider("Number of colors", 3, 10, 5)
        
        if st.button("🎨 Generate Palette", use_container_width=True):
            try:
                with st.spinner("Generating quantum color palette..."):
                    color_gen = QuantumColorGenerator()
                    st.session_state.color_palette = color_gen.generate_palette(num_colors)
                    
            except Exception as e:
                st.error(f"Error: {str(e)}")
    
    with col2:
        if st.session_state.color_palette:
            st.subheader("Your Quantum Palette")
            
            cols = st.columns(min(5, len(st.session_state.color_palette)))
            for idx, (hex_color, rgb) in enumerate(st.session_state.color_palette):
                with cols[idx % 5]:
                    st.markdown(f"""
                    <div style='background-color: {hex_color}; padding: 60px; 
                    border-radius: 8px; margin-bottom: 5px; border: 1px solid #ddd;'></div>
                    <p style='text-align: center; font-size: 12px; margin: 0;'>{hex_color.upper()}</p>
                    """, unsafe_allow_html=True)
            
            # Export palette
            palette_text = "\n".join([f"{hex_color}: rgb{rgb}" for hex_color, rgb in st.session_state.color_palette])
            st.download_button(
                "💾 Download Palette",
                palette_text,
                file_name="quantum_palette.txt",
                mime="text/plain"
            )


def render_password_generator():
    """Render the quantum password generator page."""
    st.header("🔐 Quantum Password Generator")
    st.markdown("""
    Generate cryptographically strong passwords using quantum randomness. 
    Each character is selected through quantum measurement.
    """)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Password Settings")
        
        length = st.slider("Password Length", 8, 64, 16)
        
        use_upper = st.checkbox("Uppercase (A-Z)", value=True)
        use_lower = st.checkbox("Lowercase (a-z)", value=True)
        use_digits = st.checkbox("Digits (0-9)", value=True)
        use_special = st.checkbox("Special Characters (!@#$...)", value=True)
        
        num_passwords = st.slider("Number of Passwords", 1, 10, 1)
        
        if st.button("🔐 Generate Quantum Password(s)", type="primary", use_container_width=True):
            try:
                if not any([use_upper, use_lower, use_digits, use_special]):
                    st.warning("Please select at least one character type!")
                else:
                    with st.spinner("Generating quantum passwords..."):
                        pwd_gen = QuantumPasswordGenerator()
                        st.session_state.passwords = []
                        
                        for _ in range(num_passwords):
                            password = pwd_gen.generate_password(
                                length=length,
                                use_upper=use_upper,
                                use_lower=use_lower,
                                use_digits=use_digits,
                                use_special=use_special
                            )
                            st.session_state.passwords.append(password)
                        
            except Exception as e:
                st.error(f"Error: {str(e)}")
    
    with col2:
        if st.session_state.passwords:
            st.subheader("Generated Passwords")
            
            for idx, password in enumerate(st.session_state.passwords, 1):
                st.code(password, language="text")
            
            # Export passwords
            passwords_text = "\n".join(st.session_state.passwords)
            st.download_button(
                "💾 Download Passwords",
                passwords_text,
                file_name="quantum_passwords.txt",
                mime="text/plain"
            )
            
            st.warning("⚠️ Security Tips:")
            st.markdown("""
            - Never share passwords
            - Use unique passwords for each account
            - Store passwords in a password manager
            - Enable 2FA when available
            """)


def render_crypto_key_generator():
    """Render the cryptographic key generator page."""
    st.header("🔑 Quantum Cryptographic Key Generator")
    st.markdown("""
    Generate cryptographically secure keys using quantum randomness for various security applications.
    All keys are generated through quantum measurements for maximum entropy.
    """)
    
    # Key type selector
    key_type = st.selectbox(
        "Select Key Type",
        [
            "Symmetric Encryption Key (AES, ChaCha20)",
            "HMAC Key (Message Authentication)",
            "API Key",
            "JWT Secret",
            "Initialization Vector (IV)",
            "Salt (Password Hashing)",
            "Nonce (Authenticated Encryption)",
            "Session Token",
            "WPA/WPA2 Pre-Shared Key",
            "WEP Key"
        ]
    )
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("⚙️ Key Configuration")
        
        # Configuration based on key type
        if "Symmetric Encryption" in key_type:
            key_size = st.radio("Key Size", [128, 192, 256], index=2, horizontal=True)
            st.info(f"**AES-{key_size}** or **ChaCha20** compatible")
        
        elif "HMAC" in key_type:
            key_size = st.radio("Key Size", [128, 256, 512], index=1, horizontal=True)
            st.info("For **HMAC-SHA256** or **HMAC-SHA512**")
        
        elif "API Key" in key_type:
            key_length = st.slider("Key Length", 16, 64, 32)
            st.info("Alphanumeric characters only")
        
        elif "JWT" in key_type:
            key_size = st.radio("Key Size", [256, 384, 512], index=0, horizontal=True)
            st.info("For **HS256**, **HS384**, or **HS512** algorithms")
        
        elif "Initialization Vector" in key_type:
            key_size = st.radio("IV Size", [64, 96, 128], index=2, horizontal=True)
            st.info("For **AES-CBC**, **AES-CTR**, or **AES-GCM**")
        
        elif "Salt" in key_type:
            salt_length = st.slider("Salt Length (bytes)", 8, 32, 16)
            st.info("For **bcrypt**, **scrypt**, or **Argon2**")
        
        elif "Nonce" in key_type:
            nonce_length = st.slider("Nonce Length (bytes)", 8, 16, 12)
            st.info("For **AES-GCM** or **ChaCha20-Poly1305**")
        
        elif "Session Token" in key_type:
            token_length = st.slider("Token Length (bytes)", 16, 64, 32)
            st.info("For web session management")
        
        elif "WPA" in key_type:
            st.info("**256-bit** Pre-Shared Key for WPA2/WPA3")
            key_size = 256
        
        elif "WEP" in key_type:
            key_size = st.radio("WEP Key Size", [64, 128], index=1, horizontal=True)
            st.warning("⚠️ WEP is deprecated and insecure. Use WPA2/WPA3 instead!")
        
        # Generate button
        if st.button("🔑 Generate Quantum Key", type="primary", use_container_width=True):
            try:
                with st.spinner("Generating quantum cryptographic key..."):
                    crypto_gen = QuantumCryptoKeyGenerator()
                    
                    # Generate based on key type
                    if "Symmetric Encryption" in key_type:
                        key_hex, key_base64 = crypto_gen.generate_symmetric_key(key_size)
                        st.session_state.crypto_keys = {
                            'type': f'Symmetric {key_size}-bit',
                            'hex': key_hex,
                            'base64': key_base64
                        }
                    
                    elif "HMAC" in key_type:
                        key_hex = crypto_gen.generate_hmac_key(key_size)
                        st.session_state.crypto_keys = {
                            'type': f'HMAC {key_size}-bit',
                            'hex': key_hex,
                            'base64': None
                        }
                    
                    elif "API Key" in key_type:
                        api_key = crypto_gen.generate_api_key(key_length)
                        st.session_state.crypto_keys = {
                            'type': 'API Key',
                            'key': api_key
                        }
                    
                    elif "JWT" in key_type:
                        jwt_secret = crypto_gen.generate_jwt_secret(key_size)
                        st.session_state.crypto_keys = {
                            'type': f'JWT Secret {key_size}-bit',
                            'hex': jwt_secret,
                            'base64': None
                        }
                    
                    elif "Initialization Vector" in key_type:
                        iv = crypto_gen.generate_initialization_vector(key_size)
                        st.session_state.crypto_keys = {
                            'type': f'IV {key_size}-bit',
                            'hex': iv
                        }
                    
                    elif "Salt" in key_type:
                        salt = crypto_gen.generate_salt(salt_length)
                        st.session_state.crypto_keys = {
                            'type': f'Salt {salt_length} bytes',
                            'hex': salt
                        }
                    
                    elif "Nonce" in key_type:
                        nonce = crypto_gen.generate_nonce(nonce_length)
                        st.session_state.crypto_keys = {
                            'type': f'Nonce {nonce_length} bytes',
                            'hex': nonce
                        }
                    
                    elif "Session Token" in key_type:
                        token = crypto_gen.generate_session_token(token_length)
                        st.session_state.crypto_keys = {
                            'type': f'Session Token {token_length} bytes',
                            'hex': token
                        }
                    
                    elif "WPA" in key_type:
                        wpa_key = crypto_gen.generate_wpa_key()
                        st.session_state.crypto_keys = {
                            'type': 'WPA/WPA2 PSK',
                            'hex': wpa_key
                        }
                    
                    elif "WEP" in key_type:
                        wep_key = crypto_gen.generate_wep_key(key_size)
                        st.session_state.crypto_keys = {
                            'type': f'WEP {key_size}-bit',
                            'hex': wep_key
                        }
                    
                    st.success("✅ Quantum key generated successfully!")
                    
            except Exception as e:
                st.error(f"Error: {str(e)}")
    
    with col2:
        if 'crypto_keys' in st.session_state and st.session_state.crypto_keys:
            st.subheader("🔐 Generated Key")
            
            key_data = st.session_state.crypto_keys
            
            st.markdown(f"**Type:** {key_data['type']}")
            
            # Display key in different formats
            if 'hex' in key_data:
                st.markdown("**Hexadecimal:**")
                st.code(key_data['hex'], language="text")
                
                # Show in chunks for readability
                hex_key = key_data['hex']
                if len(hex_key) > 32:
                    st.markdown("**Formatted (16 bytes per line):**")
                    formatted = '\n'.join([hex_key[i:i+32] for i in range(0, len(hex_key), 32)])
                    st.code(formatted, language="text")
            
            if key_data.get('base64'):
                st.markdown("**Base64:**")
                st.code(key_data['base64'], language="text")
            
            if 'key' in key_data:
                st.markdown("**Key:**")
                st.code(key_data['key'], language="text")
            
            # Usage examples
            st.markdown("---")
            st.markdown("**💡 Usage Examples:**")
            
            if "Symmetric" in key_data['type']:
                st.code(f"""# Python (AES-256)
from Crypto.Cipher import AES
key = bytes.fromhex('{key_data['hex'][:64]}...')
cipher = AES.new(key, AES.MODE_GCM)

# Node.js
const crypto = require('crypto');
const key = Buffer.from('{key_data['hex'][:64]}...', 'hex');""", language="python")
            
            elif "HMAC" in key_data['type']:
                st.code(f"""# Python
import hmac
import hashlib
key = bytes.fromhex('{key_data['hex'][:64]}...')
signature = hmac.new(key, message, hashlib.sha256).hexdigest()

# Node.js
const hmac = crypto.createHmac('sha256', Buffer.from('{key_data['hex'][:64]}...', 'hex'));""", language="python")
            
            elif "API Key" in key_data['type']:
                st.code(f"""# HTTP Header
Authorization: Bearer {key_data['key']}

# Python requests
headers = {{'Authorization': 'Bearer {key_data['key']}'}}
response = requests.get(url, headers=headers)""", language="python")
            
            elif "JWT" in key_data['type']:
                st.code(f"""# Python (PyJWT)
import jwt
secret = '{key_data['hex'][:64]}...'
token = jwt.encode(payload, secret, algorithm='HS256')

# Node.js
const jwt = require('jsonwebtoken');
const token = jwt.sign(payload, '{key_data['hex'][:64]}...');""", language="python")
            
            # Download button
            export_text = f"{key_data['type']}\n{'=' * 50}\n"
            if 'hex' in key_data:
                export_text += f"Hexadecimal: {key_data['hex']}\n"
            if key_data.get('base64'):
                export_text += f"Base64: {key_data['base64']}\n"
            if 'key' in key_data:
                export_text += f"Key: {key_data['key']}\n"
            export_text += f"\nGenerated: {pd.Timestamp.now()}\n"
            export_text += "⚠️ Keep this key secure and never commit to version control!"
            
            st.download_button(
                "💾 Download Key",
                export_text,
                file_name=f"quantum_key_{key_data['type'].replace(' ', '_').lower()}.txt",
                mime="text/plain"
            )
            
            # Security warnings
            st.warning("🔒 **Security Best Practices:**")
            st.markdown("""
            - Store keys in environment variables or key management systems
            - Never hardcode keys in source code
            - Use different keys for development, staging, and production
            - Rotate keys regularly
            - Use secure key derivation for passwords (PBKDF2, bcrypt, Argon2)
            """)


def main():
    """Main Streamlit application."""
    
    # Page configuration
    st.set_page_config(
        page_title="Quantum Random Number Generator",
        page_icon="🌌",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize session state
    init_session_state()
    
    # Sidebar navigation
    st.sidebar.title("🌌 QRNG Suite")
    page = st.sidebar.radio(
        "Navigation",
        ["🎲 Random Numbers", "🎨 Color Generator", "🔐 Password Generator", "🔑 Crypto Keys"],
        label_visibility="collapsed"
    )
    
    if page == "🎲 Random Numbers":
        # Header
        st.title("🌌 Quantum Random Number Generator")
        st.markdown("""
        Generate **true random numbers** using quantum superposition! This application uses 
        Hadamard gates to place qubits in superposition states, then measures them to produce 
        genuinely random outcomes based on quantum mechanics.
        """)
        
        # Sidebar controls
        st.sidebar.header("⚙️ Configuration")
        
        num_qubits = st.sidebar.slider(
            "Number of Qubits",
            min_value=1,
            max_value=10,
            value=3,
            help="More qubits = larger random numbers (2^n possibilities)"
        )
        
        shots = st.sidebar.slider(
            "Number of Shots",
            min_value=100,
            max_value=5000,
            value=1024,
            step=100,
            help="Number of times to run the circuit for distribution analysis"
        )
        
        st.sidebar.markdown("---")
        st.sidebar.markdown(f"""
        ### 📊 Current Settings
        - **Qubits:** {num_qubits}
        - **Possible outcomes:** {2**num_qubits}
        - **Range:** 0 to {2**num_qubits - 1}
        - **Shots:** {shots}
        """)
        
        # Information section
        with st.expander("ℹ️ How It Works"):
            st.markdown("""
            ### Quantum Superposition
            1. **Initialization**: Each qubit starts in the |0⟩ state
            2. **Hadamard Gate**: Applies H-gate to create superposition: H|0⟩ = (|0⟩ + |1⟩)/√2
            3. **Measurement**: Collapses superposition to either 0 or 1 randomly
            4. **Result**: Multiple qubits create random binary strings
            
            ### Why It's Truly Random
            Unlike pseudo-random generators, quantum measurements are fundamentally random 
            according to quantum mechanics. Each outcome has equal probability (uniform distribution).
            """)
        
        # Main content area
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.header("🎲 Generate Random Number")
            
            if st.button("🚀 Generate Quantum Random Number", type="primary", use_container_width=True):
                try:
                    with st.spinner("Executing quantum circuit..."):
                        qrng = QuantumRandomGenerator(num_qubits=num_qubits)
                        binary, decimal = qrng.generate_random_number()
                        
                        # Add to history
                        st.session_state.history.append({
                            'number': decimal,
                            'binary': binary,
                            'qubits': num_qubits
                        })
                        st.session_state.total_generated += 1
                        
                        # Display result in a nice box
                        st.success("✅ Quantum number generated!")
                        
                        result_col1, result_col2 = st.columns(2)
                        with result_col1:
                            st.metric("Binary", binary)
                        with result_col2:
                            st.metric("Decimal", decimal)
                        
                        st.balloons()
                        
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
            
            # Generation history
            if st.session_state.history:
                st.subheader("📜 Generation History")
                st.caption(f"Total numbers generated: {st.session_state.total_generated}")
                
                # Show last 10 entries
                recent_history = st.session_state.history[-10:][::-1]
                history_df = pd.DataFrame(recent_history)
                history_df.index = range(len(recent_history), 0, -1)
                st.dataframe(history_df, use_container_width=True)
                
                if st.button("🗑️ Clear History"):
                    st.session_state.history = []
                    st.session_state.total_generated = 0
                    st.rerun()
        
        with col2:
            st.header("🔬 Quantum Circuit")
            
            try:
                qrng = QuantumRandomGenerator(num_qubits=num_qubits)
                circuit_diagram = create_circuit_diagram(qrng)
                st.code(circuit_diagram, language="text")
                
                st.caption("""
                **Circuit Elements:**
                - `q`: Quantum register (qubits)
                - `c`: Classical register (measurement bits)
                - `H`: Hadamard gate (creates superposition)
                - Measurement arrow: Collapses qubit to classical bit
                """)
                
            except Exception as e:
                st.error(f"Error creating circuit: {str(e)}")
        
        # Bloch Sphere Visualization
        # st.header("🌐 Bloch Sphere Representation")
        # st.markdown("""
        # The Bloch sphere shows the quantum state of each qubit after applying Hadamard gates.
        # Each qubit is in an equal superposition of |0⟩ and |1⟩ (pointing along the X-axis).
        # """)
        
        # if st.button("🌐 Visualize Bloch Sphere", use_container_width=True):
        #     try:
        #         with st.spinner("Creating Bloch sphere visualization..."):
        #             qrng = QuantumRandomGenerator(num_qubits=min(num_qubits, 3))  # Limit to 3 for clarity
        #             fig = create_bloch_sphere_visualization(qrng)
        #             if fig:
        #                 st.pyplot(fig)
        #                 plt.close()
                        
        #                 st.info(f"""
        #                 **Interpretation:** Each sphere shows one qubit's state. After Hadamard gate:
        #                 - The state vector points along the +X axis
        #                 - This represents equal probability of measuring 0 or 1
        #                 - Upon measurement, the state collapses to |0⟩ (north pole) or |1⟩ (south pole)
        #                 """)
                        
        #                 if num_qubits > 3:
        #                     st.caption(f"Note: Showing first 3 qubits only for clarity (you selected {num_qubits} qubits)")
        #     except Exception as e:
        #         st.error(f"Error: {str(e)}")
        
        # Distribution Analysis Section
        st.header("📊 Distribution Analysis")
        st.markdown("""
        Run the quantum circuit multiple times to verify true randomness. 
        All outcomes should appear with approximately equal probability.
        """)
        
        if st.button("🔍 Analyze Distribution", type="secondary", use_container_width=True):
            try:
                with st.spinner(f"Running {shots} quantum measurements..."):
                    qrng = QuantumRandomGenerator(num_qubits=num_qubits)
                    counts = qrng.run_qrng(shots=shots)
                    stats = qrng.analyze_distribution(counts, shots)
                    
                    # Create tabs for different views
                    tab1, tab2, tab3 = st.tabs(["📈 Histogram", "📋 Data Table", "📊 Statistics"])
                    
                    with tab1:
                        fig = create_distribution_chart(counts, shots)
                        st.pyplot(fig)
                        plt.close()
                        
                        st.caption("""
                        **Ideal Distribution**: All bars should be approximately the same height, 
                        indicating uniform probability across all possible outcomes.
                        """)
                    
                    with tab2:
                        df = create_probability_dataframe(counts, shots)
                        st.dataframe(df, use_container_width=True, hide_index=True)
                        
                        # Download button
                        csv = df.to_csv(index=False)
                        st.download_button(
                            label="💾 Download Data as CSV",
                            data=csv,
                            file_name=f"qrng_distribution_{num_qubits}qubits_{shots}shots.csv",
                            mime="text/csv"
                        )
                    
                    with tab3:
                        st.subheader("Statistical Metrics")
                        
                        metric_col1, metric_col2, metric_col3 = st.columns(3)
                        
                        with metric_col1:
                            st.metric("Expected Count", f"{stats['expected_count_per_outcome']:.1f}")
                            st.metric("Mean Count", f"{stats['mean_count']:.1f}")
                        
                        with metric_col2:
                            st.metric("Std Deviation", f"{stats['std_deviation']:.2f}")
                            st.metric("Chi-Squared", f"{stats['chi_squared']:.2f}")
                        
                        with metric_col3:
                            st.metric("Min Count", stats['min_count'])
                            st.metric("Max Count", stats['max_count'])
                        
                        # Randomness assessment
                        expected = stats['expected_count_per_outcome']
                        relative_std = (stats['std_deviation'] / expected) * 100
                        
                        st.subheader("✅ Randomness Assessment")
                        
                        if relative_std < 10:
                            st.success(f"**Excellent uniformity!** (σ/μ = {relative_std:.1f}%)")
                            st.markdown("The distribution shows excellent quantum randomness.")
                        elif relative_std < 20:
                            st.info(f"**Good uniformity** (σ/μ = {relative_std:.1f}%)")
                            st.markdown("The distribution shows good quantum randomness.")
                        else:
                            st.warning(f"**Fair uniformity** (σ/μ = {relative_std:.1f}%)")
                            st.markdown("Consider increasing the number of shots for better statistics.")
                        
                        # Explanation
                        with st.expander("📖 Understanding the Metrics"):
                            st.markdown("""
                            - **Expected Count**: Theoretical count per outcome for uniform distribution
                            - **Mean Count**: Average count across all outcomes
                            - **Standard Deviation**: Measure of spread from expected value
                            - **Chi-Squared**: Test statistic for uniformity (lower is more uniform)
                            - **Relative Std (σ/μ)**: Standard deviation as percentage of mean
                                - < 10%: Excellent uniformity
                                - 10-20%: Good uniformity
                                - > 20%: May need more shots
                            """)
                    
            except Exception as e:
                st.error(f"❌ Error during analysis: {str(e)}")
        
        # Footer
        st.markdown("---")
        st.markdown("""
        <div style='text-align: center'>
            <p>Built with Qiskit and Streamlit | Using quantum superposition for true randomness</p>
            <p>💡 <strong>Tip:</strong> Higher qubit counts produce larger random numbers, 
            while more shots improve statistical accuracy</p>
        </div>
        """, unsafe_allow_html=True)
    
    elif page == "🎨 Color Generator":
        render_color_generator()
    
    elif page == "🔐 Password Generator":
        render_password_generator()
    
    elif page == "🔑 Crypto Keys":
        render_crypto_key_generator()


if __name__ == "__main__":
    main()
