// Bell state (2 qubits)
OPENQASM 3.0;
include "stdgates.inc";
qubit[2] q;
/* Start group Superposition */
  h q[0];
/* End group Superposition */
/* Start group Entanglement */
  cx q[0], q[1];
/* End group Entanglement */
/* Measurement */
bit[2] c = measure q;
