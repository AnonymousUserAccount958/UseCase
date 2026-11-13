# Transparent Abstraction: Relating Quantum Low-Code Models, Code, and Mathematics

This folder contains the artifacts for the paper *Teaching Quantum Software Engineering:
Relating Quantum Low-Code Models, Code, and Mathematics*:

| Path | Content |
| --- | --- |
| [`docker-compose.yml`](docker-compose.yml) | Starts the quantum low-code modeler with the derivation view and the backend that generates the OpenQASM 3 code |
| [`modeler.env`](modeler.env) | Configuration of the modeler |
| [`use-case/`](use-case) | Use case of Section IV (faulty Grover oracle): models of the steps, screenshots, and a step-by-step walkthrough |
| [`qasm/`](qasm) | OpenQASM 3 snippets of the validation (Section V-A), grouped into their parts |
| [`validation/`](validation) | Scripts that generate the snippets with Qiskit and check the derivation against Qiskit, incl. a Docker setup |

## Starting the Environment

Requirements: [Docker](https://docs.docker.com/get-docker/) with Docker Compose.

```bash
cd 2027-qse
docker compose up --build
```

The first start builds the modeler from its sources, which takes a few minutes. By default,
the sources are fetched from the
[modeler repository](https://github.com/AnonymousUserAccount958/quantum-low-code-modeler); to use a
local copy instead, set `MODELER_SOURCES` (e.g., in a `.env` file next to
`docker-compose.yml`):

```bash
MODELER_SOURCES=../path/to/quantum-low-code-modeler
```

 Afterwards, the following services are available:

| Service | URL | Purpose |
| --- | --- | --- |
| `modeler` | <http://localhost:4242> | Quantum low-code modeler incl. the derivation view |
| `backend` | <http://localhost:8000> | Transforms models into OpenQASM 3 code with node markers |
| `backend-db` | – | Database of the backend |

The step-wise derivation, its simulator, the Bloch spheres, and the histogram run entirely in
the browser, so no further services (e.g., for execution on quantum devices) are required.
The LLM-based verbalization was disabled in the user study and needs no API token.
Another image of the backend can be used by setting `BACKEND_IMAGE`.

To stop the environment, run `docker compose down`.

## Validation Snippets

The validation covers circuits frequently encountered in quantum computing courses with
2 to 16 qubits. Each snippet was generated with Qiskit, exported as OpenQASM 3, and grouped
into its parts as an instructor would. Groups are given by comment markers, which keep the
code valid OpenQASM 3 and can be nested:

```qasm
/* Start group Grover */
  /* Start group Oracle */
    cz q[0], q[1];
  /* End group Oracle */
/* End group Grover */
```

| Snippet | Qubits | Gates | Groups (nesting by indentation) | Final state (q0 leftmost) |
| --- | --- | --- | --- | --- |
| [`01_bell_state`](qasm/01_bell_state.qasm) | 2 | 2 | Superposition, Entanglement | 1/√2 (\|00⟩ + \|11⟩) |
| [`02_ghz_state_16`](qasm/02_ghz_state_16.qasm) | 16 | 16 | Superposition, Entanglement | 1/√2 (\|0…0⟩ + \|1…1⟩) |
| [`03_deutsch_jozsa`](qasm/03_deutsch_jozsa.qasm) | 4 | 11 | Initialization, Oracle, Interference | \|111⟩ ⊗ \|−⟩, i.e., the balanced oracle f(x) = x0 ⊕ x1 ⊕ x2 |
| [`04_qft`](qasm/04_qft.qasm) | 4 | 14 | Input \|0101>, QFT (Rotations q0 … q3, Swaps) | 1/4 Σₖ e^(2πi·5k/16) \|k⟩ |
| [`05_grover_2`](qasm/05_grover_2.qasm) | 2 | 12 | Grover (Superposition, Oracle, Diffusion) | \|11⟩ (up to a global phase) |
| [`06_grover_3`](qasm/06_grover_3.qasm) | 3 | 43 | Grover (Superposition, Iteration 1 (Oracle, Diffusion), Iteration 2 (Oracle, Diffusion)) | \|101⟩ with probability ≈ 0.945 |
| [`07_w_state`](qasm/07_w_state.qasm) | 3 | 5 | Amplitude distribution, Entanglement, Basis correction | 1/√3 (\|100⟩ + \|010⟩ + \|001⟩) |
| [`08_basis_encoding`](qasm/08_basis_encoding.qasm) | 4 | 3 | Basis encoding \|1011> | \|1011⟩ |
| [`09_draper_adder`](qasm/09_draper_adder.qasm) | 6 | 23 | Encode a = 3, Encode b = 2, Adder (QFT(b), Add a, Inverse QFT(b)) | \|011⟩ ⊗ \|101⟩, i.e., a = 3, b = a + b = 5 |

The modeler orders the qubits with q0 leftmost, i.e., |q0 q1 … q(n−1)⟩, whereas Qiskit
puts q0 rightmost. Registers are read with the first qubit as the most significant bit.

Each snippet ends with a measurement, so the result of an execution can be compared
directly with the expected outcome. Outcomes are written c[0] leftmost; Qiskit's counts
write them in reverse order (only `08_basis_encoding` differs: `1101` in Qiskit).

| Snippet | Measured | Expected outcome |
| --- | --- | --- |
| `01_bell_state` | q0, q1 | `00` and `11`, 50 % each |
| `02_ghz_state_16` | all 16 | `0…0` and `1…1`, 50 % each |
| `03_deutsch_jozsa` | inputs q0–q2 (q3 is the ancilla in \|−⟩) | `111` with 100 %, i.e., balanced (only `000` would mean constant) |
| `04_qft` | q0–q3 | all 16 outcomes, 6.25 % each (the QFT is in the phases, see the final state) |
| `05_grover_2` | q0, q1 | `11` with 100 % |
| `06_grover_3` | q0–q2 | `101` with ≈ 94.5 %, the other 7 outcomes ≈ 0.8 % each |
| `07_w_state` | q0–q2 | `100`, `010`, `001`, 33.3 % each |
| `08_basis_encoding` | q0–q3 | `1011` with 100 % |
| `09_draper_adder` | result register b = q3–q5 | `101` with 100 %, i.e., b = 3 + 2 = 5 |

### Importing a Snippet

1. Open the modeler at <http://localhost:4242>.
2. Open the OpenQASM editor, paste the content of a snippet, and click
   **Apply to Canvas**.
3. The circuit appears on the canvas with one group per marked part. The derivation view
   structures its steps like these groups, so that each group can be collapsed to a single
   step and pulled down to its gates again.

### Reproducing the Validation

The validation compares, for every step i, the state computed by the modeler's simulator
with the state that Qiskit's `Statevector` computes after the first i gates (up to a
global phase), and checks that every gate is imported into the group given in the code.
It also checks the measurement: the imported Measurement block measures the qubits given in
the code, and the outcome probabilities of the modeler's simulator match Qiskit's. It can
be run either in Docker or locally.

#### With Docker

No local Python or Node installation is required:

```bash
cd 2027-qse
docker compose run --rm --build validation
```

The image exports the snippets anew with Qiskit, checks that the snippets in `qasm/`
match this export exactly, and then imports every snippet with the importer and simulator
of the modeler. The `qasm/` folder is mounted into the container, so changes to the
snippets are validated without rebuilding the image. The service belongs to the
`validation` profile and is therefore not started by `docker compose up`.

#### Locally

Requirements: Python 3.10+ and Node 20+ with the dependencies of the modeler (`pnpm install`
in the parent folder).

```bash
# 1. Generate the snippets and the Qiskit reference states (validation/reference.json)
pip install -r validation/requirements.txt
python validation/generate_qasm.py

# 2. Import every snippet with the modeler's importer and simulator, compare with Qiskit
#    (run from the parent folder after "pnpm install")
cd ..
npx --yes esbuild@0.25.12 2027-qse/validation/validate.ts --bundle --platform=node \
  --tsconfig=tsconfig.json --outfile=2027-qse/validation/validate.cjs
cd 2027-qse
node validation/validate.cjs
```

Expected output:

```text
ok   01_bell_state: 2 qubits, 2 steps, min. fidelity 1.000000000000, measured q[0,1] -> 00 50.00%, 11 50.00%
ok   02_ghz_state_16: 16 qubits, 16 steps, min. fidelity 1.000000000000, measured q[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15] -> 0000000000000000 50.00%, 1111111111111111 50.00%
ok   03_deutsch_jozsa: 4 qubits, 11 steps, min. fidelity 1.000000000000, measured q[0,1,2] -> 111 100.00%
ok   04_qft: 4 qubits, 14 steps, min. fidelity 1.000000000000, measured q[0,1,2,3] -> 0000 6.25%, 0001 6.25%, 0010 6.25%, 0011 6.25%, … (16 outcomes)
ok   05_grover_2: 2 qubits, 12 steps, min. fidelity 1.000000000000, measured q[0,1] -> 11 100.00%
ok   06_grover_3: 3 qubits, 43 steps, min. fidelity 1.000000000000, measured q[0,1,2] -> 101 94.53%, 000 0.78%, 001 0.78%, 010 0.78%, … (8 outcomes)
ok   07_w_state: 3 qubits, 5 steps, min. fidelity 1.000000000000, measured q[0,1,2] -> 001 33.33%, 010 33.33%, 100 33.33%
ok   08_basis_encoding: 4 qubits, 3 steps, min. fidelity 1.000000000000, measured q[0,1,2,3] -> 1011 100.00%
ok   09_draper_adder: 6 qubits, 23 steps, min. fidelity 1.000000000000, measured q[3,4,5] -> 101 100.00%
```

The script additionally prints the imported groups with their nesting.
