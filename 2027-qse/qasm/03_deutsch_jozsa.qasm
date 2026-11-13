// Deutsch-Jozsa, balanced oracle f(x) = x0 xor x1 xor x2 (4 qubits)
OPENQASM 3.0;
include "stdgates.inc";
qubit[4] q;
/* Start group Initialization */
  x q[3];
  h q[0];
  h q[1];
  h q[2];
  h q[3];
/* End group Initialization */
/* Start group Oracle */
  cx q[0], q[3];
  cx q[1], q[3];
  cx q[2], q[3];
/* End group Oracle */
/* Start group Interference */
  h q[0];
  h q[1];
  h q[2];
/* End group Interference */
/* Measurement of the input qubits (q[3] is the ancilla in |->) */
bit[3] c;
c[0] = measure q[0];
c[1] = measure q[1];
c[2] = measure q[2];
