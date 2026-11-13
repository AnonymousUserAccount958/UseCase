# Builds the quantum low-code modeler incl. the derivation view.
# The sources are fetched from MODELER_REPO (git URL, optionally with #branch) by BuildKit
# itself, so no local copy of the modeler is needed. Passing the git URL as build context
# instead fails with Docker Compose on Windows ("failed to evaluate path").

FROM scratch AS modeler
ARG MODELER_REPO=https://github.com/AnonymousUserAccount958/quantum-low-code-modeler.git#main
ADD ${MODELER_REPO} /

FROM node:20-alpine
WORKDIR /low-code-modeler
RUN npm install -g pnpm@9.15.2
COPY --from=modeler package.json pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile
COPY --from=modeler / ./
EXPOSE 4242
CMD ["pnpm", "run", "exposed-port"]
