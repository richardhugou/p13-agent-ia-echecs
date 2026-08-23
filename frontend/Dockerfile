# Étape 1 — l'atelier : compiler la bibliothèque échiquier puis l'application.
# node_modules (~700 Mo) reste ici, il ne part jamais dans l'image finale.
FROM node:22-slim AS atelier
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
RUN npm run build

# Étape 2 — la vitrine : nginx ne sert que les fichiers statiques compilés.
FROM nginx:1.27-alpine
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=atelier /app/dist/chess-board /usr/share/nginx/html
EXPOSE 4200
