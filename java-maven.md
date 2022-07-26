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

Dump (update this)
- `mvn -X -pl a-common-test test -Dtest=ConfigTest > /tmp/debug_config.out`
