
Test Read File
```
    @Test
    public void testReadFile() throws IOException {
        Object obj = Util.getDefaultObjectMapper().readValue(ClassLoader.getSystemClassLoader().getResourceAsStream("BUSINESS_UNITS.json"), Object.class);
        log.info(String.valueOf(obj));
    }
```

Util Class
```
@Slf4j
public class Util {

    public static String getBasicAuthHeader(@NonNull String username, @NonNull String password) {
        String token = Base64.getEncoder().encodeToString((username + ':' + password).getBytes(StandardCharsets.UTF_8));
        return "Basic " + token;
    }
    public static String getBasicAuthHeader(@NonNull PasswordCredential credential) {
        return getBasicAuthHeader(credential.getUsername(), credential.getPassword());
    }

    public static ZonedDateTime convertEpochToZonedDateTime(String epoch) {
        long longValue = Long.parseLong(epoch);
        return convertEpochToZonedDateTime(longValue);
    }

    public static ZonedDateTime convertEpochToZonedDateTime(long epoch) {

        if (epoch != 0) {
            return Instant.ofEpochMilli(epoch).atZone(Constant.PST_ZONED_ID);
        }
        return null;
    }

    public static ZonedDateTime convertEpochToZonedDateTime(String epoch1, String epoch2) {

        Long longValue = Long.parseLong(epoch1) + Long.parseLong(epoch2);
        if (longValue != 0) {
            return Instant.ofEpochMilli(longValue).atZone(Constant.PST_ZONED_ID);
        }
        return null;
    }

    public static Map<String, Boolean> simpleObjectCompare(Object obj1, Object obj2, String[] fieldNames, ObjectMapper objectMapper) {
        try {
            Map<String, Boolean> result = new HashMap<>();
            ObjectNode node1 = objectMapper.valueToTree(obj1);
            ObjectNode node2 = objectMapper.valueToTree(obj2);
            for (String fieldName : fieldNames) {
                JsonNode nodeValue1 = node1.get(fieldName);
                JsonNode nodeValue2 = node2.get(fieldName);
                if (nodeValue1 == null && nodeValue2 == null) {
                    result.put(fieldName, Boolean.TRUE);
                } else if (nodeValue1 == null || nodeValue2 == null) {
                    result.put(fieldName, Boolean.FALSE);
                } else if (!nodeValue1.asText().equalsIgnoreCase(nodeValue2.asText())) {
                    result.put(fieldName, Boolean.FALSE);
                } else {
                    result.put(fieldName, Boolean.TRUE);
                }
            }
            return result;
        } catch (Exception e) {
            throw new RuntimeException(e);
        }
    }

    public static String formatNow() {
        return formatNow(DateTimeFormatter.ISO_DATE_TIME);
    }
    public static String formatNow(String formatStr) {
        return formatNow(DateTimeFormatter.ofPattern(formatStr));
    }
    public static String formatNow(DateTimeFormatter formatter) {
        return ZonedDateTime.now().withZoneSameInstant(Constant.DEFAULT_ZONED_ID).format(formatter);
    }

    public static <I extends JsonNode> void runIfNotEmpty(I node, Consumer<I> run) {
        if (node != null && !node.isEmpty() ) {
            run.accept(node);
        }
    }
    public static Boolean isStringNullEmpty(String string) {
        return string == null || string.isEmpty() || string.trim().isEmpty();
    }

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

    public static ZonedDateTime trimZonedDateTime(String zonedDateTimeStr) {
        ZonedDateTime z = ZonedDateTime.parse(zonedDateTimeStr);
        OffsetDateTime o = z.withZoneSameInstant(ZoneId.of(z.getZone().getId())).toOffsetDateTime();
        ZonedDateTime z2 = o.toZonedDateTime();
        return z2;
    }
}
```
