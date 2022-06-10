```
ObjectMapper objectMapper = JsonMapper.builder()
            .defaultTimeZone(TimeZone.getTimeZone(Constant.DEFAULT_ZONED_ID))
            .addModule(new JavaTimeModule())
            .configure(SerializationFeature.WRITE_DATE_TIMESTAMPS_AS_NANOSECONDS, false)
            .serializationInclusion(JsonInclude.Include.NON_NULL)
            .enable(MapperFeature.SORT_PROPERTIES_ALPHABETICALLY)
            .build();
```
