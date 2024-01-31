# Don't run the batch job and just run tests

Use `properties = "spring.batch.job.enabled=false"`

```
@ExtendWith(SpringExtension.class)
@SpringBootTest(properties = "spring.batch.job.enabled=false")
@TestInstance(TestInstance.Lifecycle.PER_CLASS)
```
