// Grover search, marks |11> (2 qubits)
OPENQASM 3.0;
include "stdgates.inc";
qubit[2] q;
/* Start group Grover */
  /* Start group Superposition */
    h q[0];
    h q[1];
  /* End group Superposition */
  /* Start group Oracle */
    cz q[0], q[1];
  /* End group Oracle */
  /* Start group Diffusion */
    h q[0];
    h q[1];
    x q[0];
    x q[1];
    cz q[0], q[1];
    x q[0];
    x q[1];
    h q[0];
    h q[1];
  /* End group Diffusion */
/* End group Grover */
/* Measurement */
bit[2] c = measure q;
