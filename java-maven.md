Run a specific batch job
```
clean spring-boot:run -Dspring.batch.job.names=myBatchJob -Dspring.profiles.active=default,dev -f pom.xml
```

use maven to manage versions
- change to a new version: `mvn versions:set -DnewVersion=1.0.1-SNAPSHOT`
- revert it `mvn versions:revert` if it's not good enough
- or commit it `mvn versions:commit`
- all the above operations are locally and won't be auto committed to git (though it's named as `commit`)
