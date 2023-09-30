ServiceNow Service
```
@Slf4j
public class SnowService extends WebService {

    // 2021-06-16 16:10:43
    private static final String SNOW_DATETIME_PATTERN = "yyyy-MM-dd HH:mm:ss";
    private static final ZoneId SNOW_TIMEZONE = Constant.PST_ZONED_ID;

    private String authHeader;

    public SnowService(WebTarget webTarget, PasswordCredential credential) {
        super(webTarget);
        this.authHeader = Util.getBasicAuthHeader(credential);
    }

    SnowTicketListResponse get(String query, String tableName) {
        Map<String, ?> properties = webTarget.getConfiguration().getProperties();

        String resp = webTarget.path("/api/now/table/" + tableName)
                .queryParam("sysparm_view", "standard")
                .queryParam("sysparm_display_value", true)
                .queryParam("sysparm_exclude_reference_link", true)
                .queryParam("sysparm_query", query)
                .request()
                .header("Authorization", authHeader)
                .get(String.class);
        log.info(resp.substring(0, Math.min(200, resp.length())));
        try {
            return objectMapper.readValue(resp, SnowTicketListResponse.class);
        } catch (Exception ex) {
            throw new RuntimeException(ex);
        }
    }

    public Set<SnowTicket> getChangeTickets(ZonedDateTime startTime, ZonedDateTime endTime, ChangeType changeType) {
        List<String> queryItems = new ArrayList<>();
        queryItems.add(String.format("sys_created_on>=%s", convertToSnowTimeString(startTime)));
        queryItems.add(String.format("sys_created_on<%s", convertToSnowTimeString(endTime)));

        switch (changeType) {
            // https://service-now.com/nav_to.do?uri=%2Fchange_request_list.do%3Fsysparm_query%3Dsys_created_on%253E%253Djavascript:gs.dateGenerate(%25272022-08-31%2527%252C%252700:00:00%2527)%255Esys_created_on%253Cjavascript:gs.dateGenerate(%25272022-09-01%2527%252C%252700:00:00%2527)%255Eassignment_group%253D8f3bf14d1bb50454e5ef866ecc4bcb10%255Ex__core_config_subtypeINdeployment%252Cenable___disable_traffic_on_host%252Creboot%255Eshort_descriptionLIKEDeploySoftware%255Ex__change_mgmt_environment%253DProduction%26sysparm_first_row%3D1%26sysparm_view%3D
            case Code:
                queryItems.add("assignment_group=8f3bf14d1bb50454e5ef866ecc4bcb10"); // assignment_group = Altus Deployment
                queryItems.add("x__core_config_subtypeINdeployment,execute_url,refresh,reboot,enable___disable_traffic_on_host");
                queryItems.add("short_descriptionLIKEDeploySoftware");
                queryItems.add("x__change_mgmt_environment=Production");
                break;
            // v1
            case CODE_ROLL:
                queryItems.add("assigned_to=69d56947dbb87410e6be3dc4e2961979");     // assigned_to = MFE Service Account
                queryItems.add("x__core_config_category=mfe_tool");             // category = mfe_tool
                break;
            // https://service-now.com/api/now/table/change_request?sysparm_view=standard&sysparm_display_value=true&sysparm_exclude_reference_link=true&sysparm_query=sys_created_on%3E=javascript:gs.dateGenerate(%272021-12-29%27,%2708:32:26%27)^sys_created_on%3Cjavascript:gs.dateGenerate(%272021-12-30%27,%2708:32:26%27)^assignment_group=443c6f8b1b03f704cc2da9fbbc4bcbb8
            case EP:
                queryItems.add("assignment_group=443c6f8b1b03f704cc2da9fbbc4bcbb8");    // assignment_group = Experimental Learning
                break;
            //https://service-now.com/api/now/table/change_request?sysparm_view=standard&sysparm_display_value=true&sysparm_exclude_reference_link=true&sysparm_query=sys_created_on%3E=javascript:gs.dateGenerate(%272021-12-21%27,%2708:32:26%27)^sys_created_on%3Cjavascript:gs.dateGenerate(%272021-12-30%27,%2708:32:26%27)^assigned_to=69d56947dbb87410e6be3dc4e2961979
            case Config:
                queryItems.add("assigned_to=69d56947dbb87410e6be3dc4e2961979");     // assigned_to = MFE Service Account
                queryItems.add("x_core_config_category=mfe_tool");             // category = mfe_tool
                break;
                // v1
            case MFE_CONFIG:
                queryItems.add("assigned_to=69d56947dbb87410e6be3dc4e2961979");     // assigned_to = MFE Service Account
                queryItems.add("x__core_config_category=mfe_tool");             // category = mfe_tool
                break;
            // UI: https://service-now.com/nav_to.do?uri=%2Fchange_request.do%3Fsys_id%3D4fea571587aa01d03dc8866d8bbb35b9%26sysparm_record_list%3Dx__core_config_categoryINdss%255eORDERBYDESCsys_updated_on%26sysparm_record_row%3D1%26sysparm_record_rows%3D884%26sysparm_record_target%3Dchange_request%26sysparm_view%3DStandard%26sysparm_view_forced%3Dtrue
            // API: https://inc.service-now.com/api/now/embeddedhelp/change_request_list/normal?uri=%2Fchange_request_list.do%3Fsysparm_query%3Dx__core_config_categoryINdss%26sysparm_first_row%3D1%26sysparm_view%3D%26sysparm_choice_query_raw%3Dx__core_config_categorySTARTSWITHDSS%26sysparm_list_header_search%3Dtrue
            case DSS:
                queryItems.add("x__core_config_category=DSS");             // category = DSS
                break;
            // UI: https://service-now.com/nav_to.do?uri=%2Fchange_request_list.do%3Fsysparm_query%3Dx__core_config_typeINdata_platforms_rheos_streaming%26sysparm_first_row%3D1%26sysparm_view%3D
            case Rheos:
                queryItems.add("x__core_config_typeINdata_platforms_rheos_streaming"); // Type = Rheos Streaming, Subtype = Streaming Service Operation
                break;
            default:
                break;
        }

        String q = String.join("^", queryItems);
        SnowTicketListResponse resp = getChangeTickets(q);
        if (resp == null || resp.getResult() == null) {
            return new HashSet<>();
        }
        return resp.getResult();
    }

    public SnowTicket getSingleTicketById(String ticketId) {
        List<String> queryItems = new ArrayList<>();
        queryItems.add("number=" + ticketId);
        String q = String.join("^", queryItems);
        SnowTicketListResponse resp = getChangeTickets(q);
        if (resp == null || resp.getResult() == null || resp.getResult().isEmpty()) {
            return null;
        }
        return resp.getResult().iterator().next();
    }

    SnowTicketListResponse getIncidents(String query) {
        return get(query, "incident");
    }

    SnowTicketListResponse getChangeTickets(String query) {
        return get(query, "change_request");
    }

```


Use offset for storing in database: https://www.baeldung.com/java-zoneddatetime-offsetdatetime

1. 
Output: `javascript:gs.dateGenerate('2022-06-16','15:44:06')`
Use for service now: `sys_created_on>=javascript:gs.dateGenerate('2022-06-16','15:44:06')`

```    
    private String convertToSnowTimeString(ZonedDateTime dateTime) {
        ZonedDateTime dateTimeInSnowTimeZone = dateTime.withZoneSameInstant(Constant.PST_ZONED_ID);
        return String.format("javascript:gs.dateGenerate('%s-%02d-%02d','%02d:%02d:%02d')",
                dateTimeInSnowTimeZone.getYear(),
                dateTimeInSnowTimeZone.getMonthValue(),
                dateTimeInSnowTimeZone.getDayOfMonth(),
                dateTimeInSnowTimeZone.getHour(),
                dateTimeInSnowTimeZone.getMinute(),
                dateTimeInSnowTimeZone.getSecond()
        );
    }
```

ServiceNow Model 
```
@Slf4j
@Data
@JsonIgnoreProperties(ignoreUnknown = true)
public class SnowTicket {
    public static final String SNOW_EP_LAST_UPDATE_TIME_DATETIME_PATTERN_WITH_MILLI = "yyyy-MM-dd'T'HH:mm:ss.SSS";
    public static final String SNOW_EP_LAST_UPDATE_TIME_DATETIME_PATTERN = "yyyy-MM-dd'T'HH:mm:ss";

    @JsonProperty("start_date")
    String startDate;

    @JsonProperty("end_date")
    String endDate;

    @JsonProperty("work_start")
    String workStart;

    @JsonProperty("work_end")
    String workEnd;

    String number;
    String state;
    String risk;

    @JsonProperty("close_code")
    String closeCode;

    @JsonProperty("caller_id")
    String callerId;

    @JsonProperty("short_description")
    String shortDescription;

    @JsonProperty("assignment_group")
    String assignmentGroup;

    @JsonProperty("assigned_to")
    String assignedTo;

    @JsonProperty("requested_by")
    String requestedBy;

    @JsonProperty("x__change_mgmt_environment")
    String xChangeMgmtEnvironment;

    @JsonProperty("x__change_mgmt_ci_component")
    String xChangeMgmtCiComponent;

    @JsonProperty("x__core_config_subtype")
    String xCoreConfigSubtype;

    @JsonProperty("sys_created_on")
    String createAt;

    @JsonProperty("sys_created_by")
    String createdBy;

    Object rawExperiment;

    @JsonProperty("implementation_plan")
    Object implementationPlan;

    @JsonProperty("backout_plan")
    Object rollbackPlan;
}

```

2. 
// 2021-06-16 16:10:43
```
private static final String SNOW_DATETIME_PATTERN = "yyyy-MM-dd HH:mm:ss";
private static final ZoneId SNOW_TIMEZONE = Constant.PST_ZONED_ID;
```
Output: (ZonedDateTime) "2022-06-17T13:13:52-07:00[America/Los_Angeles]"
```
    public static ZonedDateTime convertFromSnowTimeString(String snowTimeString) {
        if (snowTimeString == null || snowTimeString.isEmpty()) {
            return null;
        }
        DateTimeFormatter formatter = DateTimeFormatter.ofPattern(SNOW_DATETIME_PATTERN);
        LocalDateTime localDateTime = LocalDateTime.parse(snowTimeString, formatter);
        return localDateTime.atZone(SNOW_TIMEZONE);
    }
```
3.
Output: (ZonedDateTime) "2022-06-17T13:13:52-07:00"
```
    public static ZonedDateTime convertFromSnowTimeString(String snowTimeString) {
        if (snowTimeString == null || snowTimeString.isEmpty()) {
            return null;
        }
        DateTimeFormatter formatter = DateTimeFormatter.ofPattern(SNOW_DATETIME_PATTERN);
        LocalDateTime localDateTime = LocalDateTime.parse(snowTimeString, formatter);
        String offset = localDateTime.atZone(SNOW_TIMEZONE).getOffset().toString();
        return localDateTime.atOffset(ZoneOffset.of(offset)).toZonedDateTime();
    }
```
