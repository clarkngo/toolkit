Using `@Autowired`, you need to first add `@Component` to the class

Using `@EnableBatchProccessing`, you need to add `starter-batch`. There's a version that doesn't have it.
```
		<dependency>
			<groupId>org.springframework.boot</groupId>
			<artifactId>spring-boot-starter-batch</artifactId>
		</dependency>
```
