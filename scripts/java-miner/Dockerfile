
# Build Stage
FROM maven:3.8-openjdk-17-slim AS build
COPY src /home/app/src
COPY pom.xml /home/app
RUN mvn -f /home/app/pom.xml clean package

# Execution Stage
FROM openjdk:17-oracle
COPY --from=build /home/app/target/youtube-miner-0.0.1-SNAPSHOT.jar /usr/local/lib/youtube-miner-0.0.1-SNAPSHOT.jar
EXPOSE 8080
ENTRYPOINT ["java","-jar","/usr/local/lib/youtube-miner-0.0.1-SNAPSHOT.jar"]