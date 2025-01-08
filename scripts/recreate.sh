# Delete the old container and volume
docker rm -f quark-apps-server
docker rm -f quark-apps-server-db

# run the new container
docker compose up -d