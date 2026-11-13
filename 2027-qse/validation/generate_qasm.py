"""Builds the validation circuits with Qiskit, exports them as OpenQASM 3 and inserts
group markers (/* Start group <label> */ ... /* End group <label> */)."""
import json, math, sys
from contextlib import contextmanager
from pathlib import Path
from qiskit import QuantumCircuit, QuantumRegister, qasm3
from qiskit.quantum_info import Statevector

HERE = Path(__file__).resolve().parent
OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE.parent / "qasm"
REFERENCE = Path(sys.argv[2]) if len(sys.argv) > 2 else HERE / "reference.json"
OUT.mkdir(parents=True, exist_ok=True)


class Grouped:
    def __init__(self, n):
        self.qc = QuantumCircuit(QuantumRegister(n, "q"))
        self.markers = []  # (gate index, text)
        # measured qubits (c[i] = measure q[measured[i]]) and the comment above them;
        # written after the circuit, not part of qc, so the steps are the gates only
        self.measured = list(range(n))
        self.measure_comment = "Measurement"

    def measure(self, qubits, comment):
        self.measured = list(qubits)
        self.measure_comment = comment

    def measurement_lines(self):
        n, k = self.qc.num_qubits, len(self.measured)
        lines = [f"/* {self.measure_comment} */"]
        if self.measured == list(range(n)):
            return lines + [f"bit[{n}] c = measure q;"]
        return lines + [f"bit[{k}] c;"] + [
            f"c[{i}] = measure q[{q}];" for i, q in enumerate(self.measured)
        ]

    @contextmanager
    def group(self, label):
        self.markers.append((len(self.qc.data), f"/* Start group {label} */"))
        yield
        self.markers.append((len(self.qc.data), f"/* End group {label} */"))

    def qasm(self, title):
        lines = qasm3.dumps(self.qc).strip().splitlines()
        decl = next(i for i, l in enumerate(lines) if l.startswith("qubit["))
        head, body = lines[: decl + 1], lines[decl + 1 :]
        assert len(body) == len(self.qc.data), (title, body)
        out = [f"// {title}"] + head
        depth = 0
        for i in range(len(body) + 1):
            for idx, text in self.markers:
                if idx == i:
                    if "End group" in text:
                        depth -= 1
                    out.append("  " * depth + text)
                    if "Start group" in text:
                        depth += 1
            if i < len(body):
                out.append("  " * depth + body[i])
        out += self.measurement_lines()
        return "\n".join(out) + "\n"


def bell():
    g = Grouped(2)
    with g.group("Superposition"):
        g.qc.h(0)
    with g.group("Entanglement"):
        g.qc.cx(0, 1)
    return g


def ghz(n=16):
    g = Grouped(n)
    with g.group("Superposition"):
        g.qc.h(0)
    with g.group("Entanglement"):
        for i in range(n - 1):
            g.qc.cx(i, i + 1)
    return g


def deutsch_jozsa():
    # 3 input qubits q0-q2, ancilla q3, balanced oracle f(x) = x0 xor x1 xor x2
    g = Grouped(4)
    with g.group("Initialization"):
        g.qc.x(3)
        for q in range(4):
            g.qc.h(q)
    with g.group("Oracle"):
        for q in range(3):
            g.qc.cx(q, 3)
    with g.group("Interference"):
        for q in range(3):
            g.qc.h(q)
    g.measure(range(3), "Measurement of the input qubits (q[3] is the ancilla in |->)")
    return g


def qft_rotations(g, qubits, inverse=False):
    """QFT on the given qubits (first qubit = most significant), with swaps."""
    n = len(qubits)
    ops = []
    for i in range(n):
        ops.append(("h", qubits[i], None, None))
        for j in range(i + 1, n):
            ops.append(("cp", qubits[j], qubits[i], math.pi / 2 ** (j - i)))
    for i in range(n // 2):
        ops.append(("swap", qubits[i], qubits[n - 1 - i], None))
    if inverse:
        ops = [(o, a, b, -t if t else t) for (o, a, b, t) in reversed(ops)]
    for o, a, b, t in ops:
        if o == "h":
            g.qc.h(a)
        elif o == "swap":
            g.qc.swap(a, b)
        else:
            g.qc.cp(t, a, b)


def qft():
    g = Grouped(4)
    with g.group("Input |0101>"):
        g.qc.x(1)
        g.qc.x(3)
    with g.group("QFT"):
        for i in range(4):
            with g.group(f"Rotations q{i}"):
                g.qc.h(i)
                for j in range(i + 1, 4):
                    g.qc.cp(math.pi / 2 ** (j - i), j, i)
        with g.group("Swaps"):
            g.qc.swap(0, 3)
            g.qc.swap(1, 2)
    return g


def diffusion_2(g):
    for q in (0, 1):
        g.qc.h(q)
    for q in (0, 1):
        g.qc.x(q)
    g.qc.cz(0, 1)
    for q in (0, 1):
        g.qc.x(q)
    for q in (0, 1):
        g.qc.h(q)


def grover_2():
    # marks |11>
    g = Grouped(2)
    with g.group("Grover"):
        with g.group("Superposition"):
            g.qc.h(0)
            g.qc.h(1)
        with g.group("Oracle"):
            g.qc.cz(0, 1)
        with g.group("Diffusion"):
            diffusion_2(g)
    return g


def ccz(g):
    g.qc.h(2)
    g.qc.ccx(0, 1, 2)
    g.qc.h(2)


def grover_3():
    # marks |101> (q0 = 1, q1 = 0, q2 = 1), two iterations
    g = Grouped(3)
    with g.group("Grover"):
        with g.group("Superposition"):
            for q in range(3):
                g.qc.h(q)
        for it in (1, 2):
            with g.group(f"Iteration {it}"):
                with g.group("Oracle"):
                    g.qc.x(1)
                    ccz(g)
                    g.qc.x(1)
                with g.group("Diffusion"):
                    for q in range(3):
                        g.qc.h(q)
                    for q in range(3):
                        g.qc.x(q)
                    ccz(g)
                    for q in range(3):
                        g.qc.x(q)
                    for q in range(3):
                        g.qc.h(q)
    return g


def w_state():
    g = Grouped(3)
    with g.group("Amplitude distribution"):
        g.qc.ry(2 * math.acos(1 / math.sqrt(3)), 0)
        g.qc.ch(0, 1)
    with g.group("Entanglement"):
        g.qc.cx(1, 2)
        g.qc.cx(0, 1)
    with g.group("Basis correction"):
        g.qc.x(0)
    return g


def basis_encoding():
    # encodes the bit string 1011 (q0 leftmost)
    g = Grouped(4)
    with g.group("Basis encoding |1011>"):
        for q, bit in enumerate("1011"):
            if bit == "1":
                g.qc.x(q)
    return g


def draper_adder(a=3, b=2, n=3):
    """b := a + b mod 2^n (Draper). a on q0..q2, b on q3..q5, q0 and q3 most significant."""
    g = Grouped(2 * n)
    A, B = list(range(n)), list(range(n, 2 * n))
    with g.group(f"Encode a = {a}"):
        for i, q in enumerate(A):
            if (a >> (n - 1 - i)) & 1:
                g.qc.x(q)
    with g.group(f"Encode b = {b}"):
        for i, q in enumerate(B):
            if (b >> (n - 1 - i)) & 1:
                g.qc.x(q)
    with g.group("Adder"):
        with g.group("QFT(b)"):
            qft_rotations(g, B)
        with g.group("Add a"):
            # after the QFT (with swaps), B[k] carries the phase 2*pi*b/2^(k+1)
            for k in range(n):
                for i in range(n):
                    weight = n - 1 - i  # a[i] has the value 2^weight
                    if weight <= k:
                        g.qc.cp(math.pi / 2 ** (k - weight), A[i], B[k])
        with g.group("Inverse QFT(b)"):
            qft_rotations(g, B, inverse=True)
    g.measure(B, "Measurement of the result register b = q[3..5] (q[0..2] still hold a)")
    return g


CIRCUITS = {
    "01_bell_state": (bell, "Bell state (2 qubits)"),
    "02_ghz_state_16": (ghz, "GHZ state (16 qubits)"),
    "03_deutsch_jozsa": (deutsch_jozsa, "Deutsch-Jozsa, balanced oracle f(x) = x0 xor x1 xor x2 (4 qubits)"),
    "04_qft": (qft, "Quantum Fourier transform of |0101> (4 qubits)"),
    "05_grover_2": (grover_2, "Grover search, marks |11> (2 qubits)"),
    "06_grover_3": (grover_3, "Grover search, marks |101>, two iterations (3 qubits)"),
    "07_w_state": (w_state, "W state (3 qubits)"),
    "08_basis_encoding": (basis_encoding, "Basis encoding of |1011> (4 qubits)"),
    "09_draper_adder": (draper_adder, "Draper QFT adder, b := a + b mod 8 with a = 3, b = 2 (6 qubits)"),
}

if __name__ == "__main__":
    reference = {}
    for name, (build, title) in CIRCUITS.items():
        g = build()
        (OUT / f"{name}.qasm").write_text(g.qasm(title), encoding="utf-8", newline="\n")
        n = g.qc.num_qubits

        def terms(qc):
            # nonzero amplitudes with q0 leftmost (the modeler's convention); Qiskit puts q0 rightmost
            return {format(i, f"0{n}b")[::-1]: [a.real, a.imag]
                    for i, a in enumerate(Statevector(qc).data) if abs(a) > 1e-12}

        steps = []
        for k in range(1, len(g.qc.data) + 1):
            prefix = QuantumCircuit(g.qc.qubits)
            for inst in g.qc.data[:k]:
                prefix.append(inst)
            steps.append(terms(prefix))
        # expected measurement result: probability of each outcome c[0] c[1] ... (c[i] is
        # measured from q[measured[i]]), written c[0] leftmost like the qubits
        probs = Statevector(g.qc).probabilities_dict(qargs=g.measured)
        outcomes = {bits[::-1]: p for bits, p in sorted(probs.items()) if p > 1e-12}
        reference[name] = {
            "numQubits": n,
            "numGates": len(g.qc.data),
            "groups": [t[len("/* Start group "):-3] for _, t in g.markers if "Start group" in t],
            "steps": steps,
            "terms": steps[-1],
            "measured": g.measured,
            "outcomes": dict(sorted(outcomes.items())),
        }
    REFERENCE.write_text(json.dumps(reference, indent=1), encoding="utf-8")

    # sanity check of the adder for all inputs
    for a in range(8):
        for b in range(8):
            probs = Statevector(draper_adder(a, b).qc).probabilities_dict()
            top = max(probs, key=probs.get)  # Qiskit order: q5 ... q0
            bits = top[::-1]  # q0 ... q5
            assert probs[top] > 0.999, (a, b, probs[top])
            assert int(bits[:3], 2) == a and int(bits[3:], 2) == (a + b) % 8, (a, b, top)
    print("adder ok for all 64 inputs")
    for k, v in reference.items():
        terms = list(v["terms"].items())
        print(k, v["numQubits"], "qubits", v["numGates"], "gates", len(terms), "terms", terms[:3],
              "outcomes", list(v["outcomes"].items())[:3])
