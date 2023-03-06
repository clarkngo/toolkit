```
@Component
@Slf4j
public class RestClient {
    private final Client client = HttpClientHelper.attachC2sProxy(ClientBuilder.newClient());

    public List<String> scrapePageContent(String url, String contentType) {
        try {
            String responseStr = client.target(url).request(contentType).get(String.class);
            return Arrays.asList(responseStr.split("\n"));
        } catch (Exception e) {
            log.error("Exception when scaping page content. URL: " + url + ", Exception: " + e);
        }
        return new ArrayList<>();
    }
}
```
