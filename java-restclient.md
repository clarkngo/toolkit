```
            String[] cmd = {"curl", url};
            // List<String> lines = console.execCurl(cmd);
            List<String> lines = client.scrapePageContent(urk, MediaType.TEXT_PLAIN);

            // Analyze the content of the curl response and store the data
            metricProvider.analyzeContent(descriptions, metrics, metricUnit, lines, name, namespace, token, pool.getApplicationId());
public class PoolService {
    private void fetchInfo(String appInfoUrl, AppInfo appInfo) {
        if (!"".equals(appBuildInfoUrl)) {
            String[] cmd = {"curl", appInfoUrl};
          //  List<String> lines = console.execCurl(cmd);
            List<String> lines = client.scrapePageContent(appInfoUrl, MediaType.APPLICATION_XML);
```

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
