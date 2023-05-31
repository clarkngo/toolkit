[Maven CLI Options Reference](https://maven.apache.org/ref/3.6.3/maven-embedder/cli.html)

Run a specific batch job
```
clean spring-boot:run -Dspring.batch.job.names=myBatchJob -Dspring.profiles.active=default,dev -f pom.xml
```

use maven to manage versions
- change to a new version: `mvn versions:set -DnewVersion=1.0.1-SNAPSHOT`
- revert it `mvn versions:revert` if it's not good enough
- or commit it `mvn versions:commit`
- all the above operations are locally and won't be auto committed to git (though it's named as `commit`)

## How to test
- run below unit test and make sure it pass
  - `mvn -pl common-test test -Dtest=GlobalConfigTest`
### Normal unit tests (with endpoints available in QA/stagging env)
- `mvn -pl common-test test "-Dtest=com.common.test.**"`
### Dev unit tests (with endpoints only available in prod env)
- add c2sProxy
- `mvn -pl common-test test "-Dtest=com.common.devtest.**"`


## POM
### xxxBean already exists ... Duplication..Exception
fix:
```
      <plugin>
        <groupId>org.apache.maven.plugins</groupId>
        <artifactId>maven-surefire-plugin</artifactId>
        <configuration>
          <reuseForks>false</reuseForks>
        </configuration>
      </plugin>
```
Reason:

In the context of the maven-surefire-plugin, the configuration <reuseForks>false</reuseForks> controls whether the plugin should reuse JVM forks for running tests.

When <reuseForks> is set to false, it means that the plugin will create a new JVM fork for each test class. This ensures that each test class runs in a clean and isolated environment. This is the default behavior of the maven-surefire-plugin when <reuseForks> is not explicitly specified.

By creating a new JVM fork for each test class, it helps avoid any potential interference or contamination between tests. If one test modifies the JVM environment (e.g., system properties, class loading, etc.), it won't affect subsequent tests.

Setting <reuseForks> to true would indicate that the plugin should reuse the same JVM fork for multiple test classes. This approach can reduce the overhead of creating new JVM instances for each test class, potentially improving build performance. However, it also introduces the risk of test pollution, where changes made by one test may unintentionally affect the execution of subsequent tests.

In most cases, it is recommended to keep <reuseForks> set to false (the default value) to ensure test isolation and maintain reliable and predictable test results.

Dump (update this)
- `mvn -X -pl a-common-test test -Dtest=ConfigTest > /tmp/debug_config.out`
