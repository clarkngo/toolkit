```
ObjectMapper objectMapper = JsonMapper.builder()
            .defaultTimeZone(TimeZone.getTimeZone(Constant.DEFAULT_ZONED_ID))
            .addModule(new JavaTimeModule())
            .configure(SerializationFeature.WRITE_DATE_TIMESTAMPS_AS_NANOSECONDS, false)
            .serializationInclusion(JsonInclude.Include.NON_NULL)
            .enable(MapperFeature.SORT_PROPERTIES_ALPHABETICALLY)
            .build();
```



```
    public static ObjectMapper getDefaultObjectMapper() {
        return JsonMapper.builder()
                .defaultTimeZone(TimeZone.getTimeZone(Constant.DEFAULT_ZONED_ID))
                .addModule(new JavaTimeModule())
                .serializationInclusion(JsonInclude.Include.NON_NULL)
                .enable(MapperFeature.SORT_PROPERTIES_ALPHABETICALLY)
                .configure(SerializationFeature.WRITE_DATE_TIMESTAMPS_AS_NANOSECONDS, false)
                .configure(DeserializationFeature.READ_DATE_TIMESTAMPS_AS_NANOSECONDS, false)
                .build();
    }
```

Convert Json Array String to Java List
```
Util.getDefaultObjectMapper().readValue(resp, TypeFactory.defaultInstance().constructCollectionType(List.class, Person.class));
```

Convert Json Array to Java List
```
Util.getDefaultObjectMapper().convertValue(someJsonArray, new TypeReference<List<KidsmenuQueryDate>>(){});
```


```

    @Test
    public void testStringToZonedDateTime() throws JsonProcessingException {
        String jsonStr = "{\"startAt\": \"2022-04-07T16:56:43-07:00\", \"requester\": \"Enze Liu\"}";
        ChangeInfo info = objectMapper.readValue(jsonStr, ChangeInfo.class);
        log.info(String.valueOf(info));

        jsonStr = "{\"startAt\": \"2022-04-07T16:56:43.123-07:00\", \"requester\": \"Enze Liu\"}";
        info = objectMapper.readValue(jsonStr, ChangeInfo.class);
        log.info(String.valueOf(info.getStartAt()));

        jsonStr = "{\"startAt\": \"2022-04-07T16:56:43.123Z\", \"requester\": \"Enze Liu\"}";
        info = objectMapper.readValue(jsonStr, ChangeInfo.class);
        log.info(String.valueOf(info.getStartAt()));

        jsonStr = "{\"startAt\": 1655602019123, \"requester\": \"Enze Liu\"}";
        info = objectMapper.readValue(jsonStr, ChangeInfo.class);
        log.info(String.valueOf(info.getStartAt()));

        jsonStr = "{\"startAt\": 1656035132000000, \"requester\": \"Enze Liu\"}";
        info = objectMapper.readValue(jsonStr, ChangeInfo.class);
        log.info(String.valueOf(info.getStartAt()));

        jsonStr = "{\"startAt\": 1656035132000, \"requester\": \"Enze Liu\"}";
        info = objectMapper.readValue(jsonStr, ChangeInfo.class);
        log.info(String.valueOf(info.getStartAt()));
    }
}
```
