// Grover search, marks |101>, two iterations (3 qubits)
OPENQASM 3.0;
include "stdgates.inc";
qubit[3] q;
/* Start group Grover */
  /* Start group Superposition */
    h q[0];
    h q[1];
    h q[2];
  /* End group Superposition */
  /* Start group Iteration 1 */
    /* Start group Oracle */
      x q[1];
      h q[2];
      ccx q[0], q[1], q[2];
      h q[2];
      x q[1];
    /* End group Oracle */
    /* Start group Diffusion */
      h q[0];
      h q[1];
      h q[2];
      x q[0];
      x q[1];
      x q[2];
      h q[2];
      ccx q[0], q[1], q[2];
      h q[2];
      x q[0];
      x q[1];
      x q[2];
      h q[0];
      h q[1];
      h q[2];
    /* End group Diffusion */
  /* End group Iteration 1 */
  /* Start group Iteration 2 */
    /* Start group Oracle */
      x q[1];
      h q[2];
      ccx q[0], q[1], q[2];
      h q[2];
      x q[1];
    /* End group Oracle */
    /* Start group Diffusion */
      h q[0];
      h q[1];
      h q[2];
      x q[0];
      x q[1];
      x q[2];
      h q[2];
      ccx q[0], q[1], q[2];
      h q[2];
      x q[0];
      x q[1];
      x q[2];
      h q[0];
      h q[1];
      h q[2];
    /* End group Diffusion */
  /* End group Iteration 2 */
/* End group Grover */
/* Measurement */
bit[3] c = measure q;
