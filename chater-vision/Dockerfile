# Use the latest Maven image with the latest OpenJDK
FROM maven:3.9.9-eclipse-temurin-23 AS build

# Set the working directory in the container
WORKDIR /app

# Copy the pom.xml file and install dependencies
COPY pom.xml .
RUN mvn dependency:go-offline -B

# Copy the source code to the container
COPY src ./src

# Package the application
RUN mvn package -DskipTests

# Use the latest OpenJDK runtime as a parent image
FROM eclipse-temurin:23-jdk-alpine

# Set the working directory in the container
WORKDIR /app

# Copy the jar file from the build stage
COPY --from=build /app/target/chater-vision-1.0-SNAPSHOT.jar /app/app.jar

# Specify the command to run the jar file
ENTRYPOINT ["java", "-jar", "app.jar"]
