// Imports every snippet with the modeler's importer and in-browser simulator and compares
// the groups and the state after every step with the Qiskit reference (see README.md).
// Optionally, a folder with freshly generated snippets is given to check that the
// snippets are exactly what generate_qasm.py exports with Qiskit.
import { existsSync, readFileSync, readdirSync } from "fs";
import { join } from "path";
import { qasmToNodes } from "@/lib/qasmToNodes";
import { parseQasm, simulate } from "@/components/utils/qasmToDirac";
import { openQasmToFlow } from "@/qasmConverter";

const [dir = "qasm", refPath = "validation/reference.json", regeneratedDir] =
  process.argv.slice(2);
const reference = JSON.parse(readFileSync(refPath, "utf-8"));
const text = (path: string) => readFileSync(path, "utf-8").replace(/\r\n/g, "\n");
let failed = 0;

for (const file of readdirSync(dir).filter((f) => f.endsWith(".qasm")).sort()) {
  const name = file.replace(/\.qasm$/, "");
  const ref = reference[name];
  const qasm = text(join(dir, file));
  if (!ref) {
    console.log(`skip ${name}: no Qiskit reference in ${refPath}`);
    continue;
  }
  const errors: string[] = [];
  if (regeneratedDir) {
    const regenerated = join(regeneratedDir, file);
    if (!existsSync(regenerated) || text(regenerated) !== qasm)
      errors.push(`differs from the Qiskit export in ${regenerated}`);
  }

  // import into the model: every group present, nested as in the code, every gate inside
  const { nodes, gateNodeIds } = qasmToNodes(qasm);
  const groups = nodes.filter((n) => n.type === "groupNode");
  const labels = groups.map((g) => g.data.label);
  if (JSON.stringify(labels) !== JSON.stringify(ref.groups))
    errors.push(`groups ${JSON.stringify(labels)} != ${JSON.stringify(ref.groups)}`);
  if (gateNodeIds.length !== ref.numGates)
    errors.push(`${gateNodeIds.length} gate nodes, expected ${ref.numGates}`);
  const byId = new Map(nodes.map((n) => [n.id, n]));
  const ungrouped = gateNodeIds.filter((id) => !byId.get(id)?.parentNode);
  if (ungrouped.length) errors.push(`${ungrouped.length} gates outside of groups`);
  const order = nodes.map((n) => n.id);
  for (const n of nodes)
    if (n.parentNode && order.indexOf(n.parentNode) > order.indexOf(n.id))
      errors.push(`parent after child: ${n.data.label}`);
  const depth = (id: string | undefined): number =>
    id ? 1 + depth(byId.get(id)?.parentNode) : 0;
  const nesting = groups.map((g) => `${"  ".repeat(depth(g.parentNode))}${g.data.label}`);

  // derivation: state of the in-browser simulator after every gate vs. Qiskit
  // (up to a global phase, i.e. the overlap |<expected|state>| must be 1)
  const parsed = parseQasm(qasm);
  if (parsed.warnings.length) errors.push(`parser warnings: ${parsed.warnings.join("; ")}`);
  const overlap = (k: number) => {
    const { sv, warnings } = simulate(parsed.numQubits, parsed.gates.slice(0, k));
    if (warnings.length) errors.push(`simulator warnings: ${warnings.join("; ")}`);
    let re = 0, im = 0;
    for (const [bits, [er, ei]] of Object.entries(ref.steps[k - 1] as Record<string, number[]>)) {
      const a = sv[parseInt(bits, 2)];
      re += er * a.re + ei * a.im;
      im += er * a.im - ei * a.re;
    }
    return Math.hypot(re, im);
  };
  let fidelity = 1;
  for (let k = 1; k <= parsed.gates.length; k++) {
    const f = overlap(k);
    fidelity = Math.min(fidelity, f);
    if (Math.abs(f - 1) > 1e-9) errors.push(`step ${k}: fidelity ${f}`);
  }

  // measurement: the imported Measurement block measures the expected qubits, and the
  // outcome probabilities of the simulator match Qiskit (c[0] written leftmost)
  const measured: number[] | undefined = ref.measured;
  const expected: Record<string, number> = ref.outcomes ?? {};
  let outcomeText = "";
  if (!measured) {
    errors.push(`no measurement in ${refPath}: regenerate it with generate_qasm.py`);
  } else {
    const block = openQasmToFlow(qasm).nodes.find((n) => n.type === "measurementNode");
    const indices = String(block?.data.indices ?? "");
    const blockQubits = indices
      ? indices.split(",").map(Number)
      : [...Array(parsed.numQubits).keys()];
    if (!block) errors.push("no Measurement block after the import");
    else if (JSON.stringify(blockQubits) !== JSON.stringify(measured))
      errors.push(`Measurement block measures [${blockQubits}], expected [${measured}]`);

    const { sv } = simulate(parsed.numQubits, parsed.gates);
    const outcomes: Record<string, number> = {};
    sv.forEach((a, i) => {
      const p = a.re * a.re + a.im * a.im;
      if (p < 1e-12) return;
      const bits = i.toString(2).padStart(parsed.numQubits, "0"); // q0 leftmost
      const key = measured.map((q) => bits[q]).join("");
      outcomes[key] = (outcomes[key] ?? 0) + p;
    });
    for (const key of new Set([...Object.keys(outcomes), ...Object.keys(expected)])) {
      const diff = Math.abs((outcomes[key] ?? 0) - (expected[key] ?? 0));
      if (diff > 1e-9)
        errors.push(`outcome ${key}: ${outcomes[key] ?? 0}, Qiskit ${expected[key] ?? 0}`);
    }
    // most likely first; equal probabilities (up to rounding) in alphabetical order
    const rounded = (p: number) => Math.round(p * 1e9);
    const shown = Object.entries(expected).sort(
      (a, b) => rounded(b[1]) - rounded(a[1]) || a[0].localeCompare(b[0]),
    );
    outcomeText = shown
      .slice(0, 4)
      .map(([k, p]) => `${k} ${(p * 100).toFixed(2)}%`)
      .join(", ") + (shown.length > 4 ? `, … (${shown.length} outcomes)` : "");
  }

  console.log(`${errors.length ? "FAIL" : "ok  "} ${name}: ${parsed.numQubits} qubits, ` +
    `${parsed.gates.length} steps, min. fidelity ${fidelity.toFixed(12)}` +
    (measured ? `, measured q[${measured}] -> ${outcomeText}` : ""));
  for (const line of nesting) console.log(`       ${line}`);
  for (const e of errors) console.log(`       ! ${e}`);
  failed += errors.length ? 1 : 0;
}
process.exit(failed ? 1 : 0);
