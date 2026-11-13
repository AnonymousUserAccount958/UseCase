# Runs the validation without a local Python or Node installation.
# Build context: the 2027-qse folder; the modeler sources are the additional build context
# "modeler" (MODELER_SOURCES), see docker-compose.yml.

# 1. Generate the snippets and the reference states with Qiskit
FROM python:3.12-slim AS qiskit
WORKDIR /validation
COPY validation/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY validation/generate_qasm.py .
RUN python generate_qasm.py /generated/qasm /generated/reference.json

# 2. Bundle the importer and simulator of the modeler with the validation script
FROM node:20-alpine
RUN npm install -g pnpm@9.15.2 esbuild@0.25.12
WORKDIR /low-code-modeler
COPY --from=modeler package.json pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile
COPY --from=modeler tsconfig.json ./
COPY --from=modeler src ./src
COPY validation/validate.ts ./2027-qse/validation/
RUN esbuild 2027-qse/validation/validate.ts --bundle --platform=node \
      --tsconfig=tsconfig.json --log-level=warning --outfile=/validation/validate.cjs

COPY --from=qiskit /generated /generated
COPY qasm /validation/qasm
WORKDIR /validation
# the snippets in /validation/qasm can be replaced by mounting another folder
CMD ["node", "validate.cjs", "qasm", "/generated/reference.json", "/generated/qasm"]
