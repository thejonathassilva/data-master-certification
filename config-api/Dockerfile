FROM maven:3.9.6-eclipse-temurin-17 AS build

ARG GITHUB_USER
ARG GITHUB_TOKEN

WORKDIR /app

RUN mkdir -p /root/.m2 && printf '%s' "\
<settings>\
  <servers>\
    <server>\
      <id>github</id>\
      <username>${GITHUB_USER}</username>\
      <password>${GITHUB_TOKEN}</password>\
    </server>\
  </servers>\
</settings>" > /root/.m2/settings.xml

COPY pom.xml .
RUN mvn -q -DskipTests --settings /root/.m2/settings.xml dependency:go-offline

# código
COPY src ./src

RUN mvn -q clean package -DskipTests --settings /root/.m2/settings.xml

# ===== Runtime =====
FROM eclipse-temurin:17-jre
WORKDIR /app

COPY --from=build /app/target/*.jar app.jar

EXPOSE 8080

ENTRYPOINT ["sh","-c","java $JAVA_OPTS -jar /app/app.jar"]
