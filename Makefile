initdb:
	docker run --name lowcode_db -p 5432:5432 -d -e POSTGRES_PASSWORD=postgres -e POSTGRES_USER=postgres -e POSTGRES_DB=lowcode postgres:16.2-alpine3.19

rmdb:
	docker rm --force lowcode_db