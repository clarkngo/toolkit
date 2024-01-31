
Elasticsearch Service
```
public class EsService extends WebService {
    String authHeader;

    ObjectMapper mapper = Util.getDefaultObjectMapper();

    public EsService(WebTarget webTarget, PasswordCredential credential) {
        super(webTarget);
        this.authHeader = Util.getBasicAuthHeader(credential);
    }
}
```

Elasticsearch Model
```
public interface QueryTerm {
    JsonNode toQuery();
}

@Data
@NoArgsConstructor
@JsonIgnoreProperties(ignoreUnknown = true)
public class RangeQuery implements QueryTerm {
    String field;
    Integer gt;
    Integer gte;
    Integer lt;
    Integer lte;

    // { "range": { "age": { "gte": 10, "lte": 20 } } }
    @Override
    public JsonNode toQuery() {
        ObjectMapper objectMapper = new ObjectMapper();
        ObjectNode result = objectMapper.createObjectNode();
        if (StringUtils.isNullOrEmpty(field)) {
            return result;
        }
        ObjectNode termNode = objectMapper.createObjectNode();
        if (gt != null) {
            termNode.put("gt", gt);
        }
        if (gte != null) {
            termNode.put("gte", gte);
        }
        if (lt != null) {
            termNode.put("lt", lt);
        }
        if (lte != null) {
            termNode.put("lte", lte);
        }
        ObjectNode rangeNode = objectMapper.createObjectNode();
        rangeNode.set(field, termNode);
        result.set("range", rangeNode);
        return result;
    }
}

@Data
@AllArgsConstructor
@JsonIgnoreProperties(ignoreUnknown = true)
public class MatchQuery implements QueryTerm {
    String key;
    String value;

    // { "match" : { "user.id" : "kimchy" } }
    @Override
    public JsonNode toQuery() {
        ObjectMapper objectMapper = new ObjectMapper();
        ObjectNode termNode = objectMapper.createObjectNode();
        termNode.put(this.key, this.value);
        ObjectNode result = objectMapper.createObjectNode();
        result.set("match", termNode);
        return result;
    }
}

@Data
@AllArgsConstructor
@JsonIgnoreProperties(ignoreUnknown = true)
public class RegexQuery implements QueryTerm {
    String key;
    String value;

    // { "term" : { "user.id" : "kimchy" } }
    @Override
    public JsonNode toQuery() {
        ObjectMapper objectMapper = new ObjectMapper();
        ObjectNode termNode = objectMapper.createObjectNode();
        termNode.put(this.key, this.value);
        ObjectNode result = objectMapper.createObjectNode();
        result.set("regexp", termNode);
        return result;
    }
}

@Data
@NoArgsConstructor
@JsonIgnoreProperties(ignoreUnknown = true)
public class SearchRequest {
    public static final String AGG_RESULT_NAME = "result";
    public static final String AGG_HITS_NAME = "hits";
    public static final String SORT_DESCENDING = "desc";
    public static final String SORT_ASCENDING = "asc";
    public static final int DEFAULT_FROM = 0;
    public static final int DEFAULT_SIZE = 300;
    public static final int MAX_SIZE = 9999;
    public static final int DEFAULT_GROUP_BY_SIZE = 999;
    private static final ObjectMapper objectMapper = new ObjectMapper();

    // refer to here: https://www.elastic.co/guide/cn/elasticsearch/guide/current/search-lite.html
    List<QueryTerm> must = new ArrayList<>();
    List<QueryTerm> mustNot = new ArrayList<>();
    Map<String, String> mustRegex = new HashMap<>();
    Map<String, Set<String>> should = new HashMap<>();
    List<Map<String, String>> multiFieldShould = new ArrayList<>();
    List<String> groupBy = new ArrayList<>();
    List<String> sumBy = new ArrayList<>();
    List<String> fields = new ArrayList<>();
    List<AggregationRequest> aggregations = new ArrayList<>();
    int from = DEFAULT_FROM;
    int size = DEFAULT_SIZE;
    String timestampFieldName;
    String sortFieldName = null;
    ZonedDateTime startTime = null;
    ZonedDateTime actualStartTime = null;
    ZonedDateTime endTime = null;
    Boolean source = null;
    String order = SORT_DESCENDING;
    DateHistogram dateHistogram;
    int groupBySize = DEFAULT_GROUP_BY_SIZE;

    private static ArrayNode queryTermListToQuery(List<QueryTerm> queryTerms) {
        ArrayNode query = objectMapper.createArrayNode();
        queryTerms.forEach(q -> query.add(q.toQuery()));
        return query;
    }

    public ObjectNode toQueryBody() {
        ObjectNode body = objectMapper.createObjectNode();
        if (this.getFrom() > 0) {
            body.put("from", this.getFrom());
        }
        body.put("size", this.getSize());
        if (this.source != null) {
            body.put("_source", this.getSource());
        }
        Util.runIfNotEmpty(toQueryNode(), q -> body.set("query", q));
        Util.runIfNotEmpty(toFieldsNode(), q -> body.set("fields", q));

        // Advanced aggregations
        if (dateHistogram != null && !aggregations.isEmpty()) {
            ObjectNode aggsResultNode = objectMapper.createObjectNode();
            aggsResultNode.set("date_histogram", this.getDateHistogram().toQuery());
            body.set("aggs", objectMapper.createObjectNode().set(AGG_RESULT_NAME, aggsResultNode));
            if (!groupBy.isEmpty()) {
                ObjectNode groupByNode = objectMapper.createObjectNode();
                aggsResultNode.set("aggs", objectMapper.createObjectNode().set(AGG_RESULT_NAME, groupByNode));
                // For now only support group by 1 dimension
                toGroupByNode(this.getGroupBy().get(0), this.getGroupBySize(), this.getSortFieldName(), this.getOrder())
                        .ifPresent(node -> groupByNode.set("terms", node));
                aggsResultNode = groupByNode;
            }
            ObjectNode finalAggsResultNode = aggsResultNode;
            toAdvancedAggregationsNode(this.getAggregations()).ifPresent(aggs -> finalAggsResultNode.set("aggs", aggs));
        } else {
            Util.runIfNotEmpty(toSortNode(), q -> body.set("sort", q));
            toAggregationNode(this.getGroupBy()).ifPresent(aggs -> body.set("aggs", aggs));
            if (!sumBy.isEmpty()) {
                toAggSumNode(this.getSumBy(), this.getSumBy()).ifPresent(aggs -> body.set("aggs", aggs));
            }
        }
        return body;
    }

    protected ArrayNode toFieldsNode() {
        ArrayNode query = objectMapper.createArrayNode();
        this.fields.forEach(query::add);
        return query;
    }

    protected Optional<ObjectNode> toAggregationNode(List<String> fieldNames) {
        if (fieldNames.isEmpty()) {
            ObjectNode s = objectMapper.createObjectNode()
                    .put("size", 1);
            Util.runIfNotEmpty(toSortNode(), q -> s.set("sort", q));
            return Optional.of(objectMapper.createObjectNode()
                    .set(AGG_HITS_NAME, objectMapper.createObjectNode().set("top_hits", s)));
        }

        ObjectNode resultNode = objectMapper.createObjectNode();

        ObjectNode terms = objectMapper.createObjectNode();
        terms.put("field", fieldNames.get(0));
        terms.put("size", groupBySize);
        resultNode.set("terms", terms);

        toAggregationNode(fieldNames.subList(1, fieldNames.size())).ifPresent(v -> resultNode.set("aggs", v));

        return Optional.of(objectMapper.createObjectNode().set(AGG_RESULT_NAME, resultNode));
    }

    protected Optional<ObjectNode> toAggSumNode(List<String> aggNames, List<String> fieldNames) {
        ObjectNode resultNode = objectMapper.createObjectNode();

        for (int i = 0; i < aggNames.size(); i++) {
            ObjectNode sum = objectMapper.createObjectNode();
            sum.put("field", fieldNames.get(i));
            ObjectNode customAgg = objectMapper.createObjectNode();
            customAgg.set("sum", sum);
            resultNode.set(aggNames.get(i), customAgg);
        }
        return Optional.of(resultNode);
    }

    private Optional<ObjectNode> toAdvancedAggregationsNode(List<AggregationRequest> aggregationRequests) {
        ObjectNode aggsNode = objectMapper.createObjectNode();
        for (AggregationRequest aggregationRequest : aggregationRequests) {
            aggsNode.set(aggregationRequest.aggName, aggregationRequest.toQueryBody());
            if (aggregationRequest.bucketSortRequest != null) {
                ObjectNode bucketSortNode = objectMapper.createObjectNode();
                bucketSortNode.set("bucket_sort", aggregationRequest.bucketSortRequest.toQueryBody());
                aggsNode.set(aggregationRequest.bucketSortRequest.bucketSortName, bucketSortNode);
            }
        }
        return Optional.of(aggsNode);
    }

    private Optional<ObjectNode> toGroupByNode(String field, int size, String sortFieldName, String order) {
        ObjectNode resultNode = objectMapper.createObjectNode();
        resultNode.put("field", field);
        if (sortFieldName != null) {
            ObjectNode orderNode = objectMapper.createObjectNode();
            orderNode.put(sortFieldName, order);
            resultNode.set("order", orderNode);
        }
        resultNode.put("size", size);
        return Optional.of(resultNode);
    }

    private ObjectNode keyValueToQuery(String key, String value) {
        ObjectNode termQuery = objectMapper.createObjectNode();
        termQuery.put(key, value);
        return objectMapper.createObjectNode().set("match", termQuery);
    }

    private ObjectNode keyValueRegexToQuery(String key, String value) {
        ObjectNode regQuery = objectMapper.createObjectNode();
        regQuery.set(key, objectMapper.createObjectNode().put("value", value));
        return objectMapper.createObjectNode().set("regexp", regQuery);
    }

    protected ArrayNode toSortNode() {
        String sort = this.sortFieldName;
        if (sort == null) {
            sort = this.timestampFieldName;
        }
        if (sort == null) {
            return null;
        }
        return objectMapper.createArrayNode()
                .add(objectMapper.createObjectNode().put(sort, order));
    }

    protected ObjectNode toQueryNode() {
        ObjectNode query = objectMapper.createObjectNode();

        // set filter
//        ArrayNode filterQuery = objectMapper.createArrayNode();
//        if (timestampFieldName != null) {
//            ObjectNode rangeQuery = objectMapper.createObjectNode();
//            ObjectNode timestampRange = objectMapper.createObjectNode();
//            if (this.getStartTime() != null) {
//                timestampRange.put("gte", this.getStartTime().toInstant().toEpochMilli());
//            }
//            timestampRange.put("lt",
//                    this.getEndTime() == null
//                            ? ZonedDateTime.now().toInstant().toEpochMilli()
//                            : this.getEndTime().toInstant().toEpochMilli());
//
//            rangeQuery.set(timestampFieldName, timestampRange);
//            filterQuery.add(objectMapper.createObjectNode().set("range", rangeQuery));
//            query.set("filter", filterQuery);
//        }

        // set must
        ArrayNode mustQuery = queryTermListToQuery(this.getMust());

        this.getShould().forEach((key, value) -> {
            ArrayNode shouldN = objectMapper.createArrayNode();
            value.forEach(v -> {
                shouldN.add(this.keyValueToQuery(key, v));
            });

            ObjectNode n = objectMapper.createObjectNode();
            n.set("should", shouldN);
            n.put("minimum_should_match", 1);
            mustQuery.add(objectMapper.createObjectNode().set("bool", n));
        });

        this.getMultiFieldShould().forEach((map) -> {
            ArrayNode shouldN = objectMapper.createArrayNode();
            map.forEach((key, value) -> {
                shouldN.add(this.keyValueToQuery(key, value));
            });
            ObjectNode n = objectMapper.createObjectNode();
            n.set("should", shouldN);
            mustQuery.add(objectMapper.createObjectNode().set("bool", n));
        });

        if (timestampFieldName != null) {
            ObjectNode rangeQuery = objectMapper.createObjectNode();
            ObjectNode timestampRange = objectMapper.createObjectNode();
            if (this.getStartTime() != null) {
                timestampRange.put("gte", this.getStartTime().toInstant().toEpochMilli());
            }
            timestampRange.put("lt",
                    this.getEndTime() == null
                            ? ZonedDateTime.now().toInstant().toEpochMilli()
                            : this.getEndTime().toInstant().toEpochMilli());
            rangeQuery.set(timestampFieldName, timestampRange);
            mustQuery.add(objectMapper.createObjectNode().set("range", rangeQuery));
        }

        Util.runIfNotEmpty(mustQuery, q -> query.set("must", q));
        Util.runIfNotEmpty(queryTermListToQuery(this.getMustNot()), q -> query.set("must_not", q));


        ObjectNode result = objectMapper.createObjectNode();
        Util.runIfNotEmpty(query, q -> result.set("bool", q));
        return result;
    }
}

```

Elasticsearch Configuration
```
@Configuration
@ConfigurationProperties(prefix="customconfig")
public class ClientConfiguration {
    @Lazy
    @Bean
    @Primary
    public EsService defaultAdsQualityEs() {
        if (isDev()) {
            Client client = HttpClientHelper.produceDefaultClient("esadsquality.esClient");
            WebTarget webTarget = HttpClientHelper.produceTarget(client);
            return injectCal(new EsService(webTarget, getPasswordCredentialBySamPath(Sam_Path)));
        } else {
            return productionAdsQualityEs();
        }
    }

    @Lazy
    @Bean(name = "productionAdsQualityEs")
    public EsService productionAdsQualityEs() {
        Client client = HttpClientHelper.produceDefaultClient("esadsquality.esClientProd");
        client.property(ClientProperties.READ_TIMEOUT, 60 * 1000);
        if (isDev()) {
            HttpClientHelper.attachC2sProxy(client);
        }
        WebTarget webTarget = HttpClientHelper.produceTarget(client);
        return injectCal(new EsService(webTarget, getPasswordCredentialBySamPath(Sam_Path)));
    }
}
```

Elasticsearch Logic
```

    public ClusterRerouteResponse clusterReroute(ClusterRerouteRequest clusterRerouteRequest) throws JsonProcessingException {
        String path = "/_cluster/reroute";
        String index1 = clusterRerouteRequest.getIndex1();
        String index2 = clusterRerouteRequest.getIndex2();
        String node1 = clusterRerouteRequest.getNode1();
        String node2 = clusterRerouteRequest.getNode2();
        int shard1 = clusterRerouteRequest.getShard1();
        int shard2 = clusterRerouteRequest.getShard2();

        Move move1 = new Move(index1, shard1, node1, node2);
        Move move2 = new Move(index2, shard2, node2, node1);

        MoveCommand moveCommand1 = new MoveCommand(move1);
        MoveCommand moveCommand2 = new MoveCommand(move2);

        CommandsObject commandsObject = new CommandsObject();
        commandsObject.setCommands(new ArrayList<>());
        commandsObject.getCommands().add(moveCommand1);
        commandsObject.getCommands().add(moveCommand2);

        String reqBody = mapper.writeValueAsString(commandsObject);

        Response resp = webTarget.path(path)
                .queryParam("metric", "none")
                .request()
                .header(HttpHeaders.CONTENT_TYPE, MediaType.APPLICATION_JSON)
                .header(HttpHeaders.AUTHORIZATION, authHeader)
                .post(Entity.entity(reqBody, MediaType.APPLICATION_JSON));

        ClusterRerouteResponse clusterRerouteResponse = new ClusterRerouteResponse();
        clusterRerouteResponse.setIndex1(index1);
        clusterRerouteResponse.setIndex2(index2);
        clusterRerouteResponse.setNode1(node1);
        clusterRerouteResponse.setNode2(node2);
        clusterRerouteResponse.setReqBody(reqBody);
        JsonNode respNode = resp.readEntity(JsonNode.class);
        clusterRerouteResponse.setResp(respNode);
        resp.close();   // avoid running out of connection
        return clusterRerouteResponse;
    }

    public ListShardsResponse listShards(ListShardsRequest listShardsRequest) {
        String path = "/_cat/shards";
        String sortOrder = listShardsRequest.getSortOrder();
        if (StringUtils.isNullOrEmpty(sortOrder)) {
            sortOrder = "desc";
        }

        log.info(webTarget.getUri().toString());
        List<Shard> shards = webTarget.path(path)
                .queryParam("v", false)
                .queryParam("s", "store:" + sortOrder)
                .queryParam("format", "json")
                .request(MediaType.APPLICATION_JSON)
                .header(HttpHeaders.CONTENT_TYPE, MediaType.APPLICATION_JSON)
                .header(HttpHeaders.AUTHORIZATION, authHeader)
                .get(new GenericType<List<Shard>>() {});

        Predicate<Shard> excludeCurrentDateIndicesFilterPredicate = shard -> false;
        Predicate<Shard> includeIndexFilterPredicate = shard -> false;
        Predicate<Shard> excludeIndexFilterPredicate = shard -> false;
        Predicate<Shard> includeNodeFilterPredicate = shard -> false;
        Predicate<Shard> excludeNodeFilterPredicate = shard -> false;
        Predicate<Shard> includeStorageSizeFilterPredicate = shard -> false;
        Predicate<Shard> excludeStorageSizeFilterPredicate = shard -> false;

        for (String includedIndex : listShardsRequest.getIncludedIndices()) {
            includeIndexFilterPredicate = includeIndexFilterPredicate.or(EsUtil.createPredicate(includedIndex, Shard::getIndex));
        }

        for (String excludedIndex : listShardsRequest.getExcludedIndices()) {
            excludeIndexFilterPredicate = excludeIndexFilterPredicate.or(EsUtil.createPredicate(excludedIndex, Shard::getIndex));
        }

        for (String includedNode : listShardsRequest.getIncludedNodes()) {
            includeNodeFilterPredicate = includeNodeFilterPredicate.or(EsUtil.createPredicate(includedNode, Shard::getNode));
        }

        for (String excludedNode : listShardsRequest.getExcludedNodes()) {
            excludeNodeFilterPredicate = excludeNodeFilterPredicate.or(EsUtil.createPredicate(excludedNode, Shard::getNode));
        }

        for (String includedStorageSize : listShardsRequest.getIncludedStorageSizes()) {
            includeStorageSizeFilterPredicate = includeStorageSizeFilterPredicate.or(EsUtil.createPredicate(includedStorageSize, Shard::getStore));
        }

        for (String excludedStorageSize : listShardsRequest.getExcludedStorageSizes()) {
            excludeStorageSizeFilterPredicate = excludeStorageSizeFilterPredicate.or(EsUtil.createPredicate(excludedStorageSize, Shard::getStore));
        }

        if (listShardsRequest.getIncludedIndices().isEmpty()) {
            includeIndexFilterPredicate = shard -> true;
        }

        if (listShardsRequest.getIncludedNodes().isEmpty()) {
            includeNodeFilterPredicate = shard -> true;
        }

        if (listShardsRequest.getIncludedStorageSizes().isEmpty()) {
            includeStorageSizeFilterPredicate = shard -> true;
        }

        shards = shards.stream().filter(includeIndexFilterPredicate.and(excludeIndexFilterPredicate.negate())
                .and(includeNodeFilterPredicate.and(excludeNodeFilterPredicate.negate()))
                .and(includeStorageSizeFilterPredicate.and(excludeStorageSizeFilterPredicate.negate())
                .and(excludeCurrentDateIndicesFilterPredicate.negate()))
        ).collect(Collectors.toList());

        if (listShardsRequest.getExcludeCurrentDateIndices()) {
            shards = shards.stream().filter(shard -> {
                String dateStr = EsUtil.extractDateString(shard.getIndex());
                if (!StringUtils.isNullOrEmpty(dateStr)) {
                    return !EsUtil.isCurrentDate(dateStr);
                }
                return true;
            }).collect(Collectors.toList());
        }

        if (listShardsRequest.getExcludeSystemIndices()) {
            shards = shards.stream().filter(shard -> {
                String index = shard.getIndex();
                if (!StringUtils.isNullOrEmpty(index)) {
                    return index.charAt(0) != '.';
                }
                return true;
            }).collect(Collectors.toList());
        }

        if (listShardsRequest.getSize() != 0) {
            shards = shards.stream()
                    .limit(listShardsRequest.getSize())
                    .collect(Collectors.toList());
        }

        String docs = listShardsRequest.getDocs();
        if (!StringUtils.isNullOrEmpty(docs)) {
            shards = shards.stream().filter(s->docs.equals(s.getDocs())).collect(Collectors.toList());
        }

        if (listShardsRequest.getComputeBytes()) {
            shards.stream().forEach(s->s.setBytes(StorageSizeConverter.convertToBytes(s.getStore())));
        }

        ListShardsResponse listShardsResponse = new ListShardsResponse();
        listShardsResponse.setShards(shards);
        listShardsResponse.setTotalShardCount(shards.size());
        return listShardsResponse;
    }

    public CandidateShardsResponse candidateShards(CandidateShardsRequest request) {
        CandidateShardsResponse resp = new CandidateShardsResponse();

        ListShardsResponse largeSizedShards = findLargeSizedShards(request);
        largeSizedShards.setTotalShardCount(largeSizedShards.getShards().size());
        ListShardsResponse smallSizedShards = findSmallSizedShards(request);


        Set<String> nodesFromLargeShardsSet  = new HashSet<>();
        if (request.getListSizeLargeShards() > 0 &&
                (!request.getCandidateIndicesOnLargeShards().isEmpty() || !request.getCandidateLargeNodes().isEmpty())) {

            for (Shard shard: largeSizedShards.getShards()) {
                nodesFromLargeShardsSet.add(shard.getNode());
            }
            nodesFromLargeShardsSet.addAll(request.getCandidateLargeNodes());

            List<Shard> smallShardsExcludingNodesFromLargeShards = smallSizedShards.getShards().stream()
                    .filter(shard -> !nodesFromLargeShardsSet.contains(shard.getNode()))
                    .collect(Collectors.toList());
            smallSizedShards.setShards(smallShardsExcludingNodesFromLargeShards);
            smallSizedShards.setTotalShardCount(smallShardsExcludingNodesFromLargeShards.size());
        }

        resp.setSmallSizedShards(new ListShardsResponse(smallSizedShards));
        resp.setLargeSizedShards(largeSizedShards);
        for (int i = 0; i < largeSizedShards.getShards().size() && 0 < smallSizedShards.getShards().size(); i++) {
            ClusterRerouteRequest sampleRequest = new ClusterRerouteRequest();
            Shard bigShard = largeSizedShards.getShards().get(i);
            sampleRequest.setIndex1(bigShard.getIndex());
            sampleRequest.setNode1(bigShard.getNode());
            sampleRequest.setShard1(bigShard.getShard());
            // Check if the small node already has a shard of bigIndex
            Set<String> unavailableNodes = listShardsForIndex(bigShard.getIndex()).getShards()
                    .stream()
                    .map(Shard::getNode)
                    .collect(Collectors.toSet());
            for (int j = 0; j < smallSizedShards.getShards().size(); j++) {
                Shard smallShard = smallSizedShards.getShards().get(j);
                if (!unavailableNodes.contains(smallShard.getNode())) {
                    // Check if the big node already has a shard of smallIndex
                    Set<String> reverseUnavailableNodes = listShardsForIndex(smallShard.getIndex()).getShards()
                            .stream()
                            .map(Shard::getNode)
                            .collect(Collectors.toSet());
                    if (!reverseUnavailableNodes.contains(bigShard.getNode())) {
                        sampleRequest.setIndex2(smallShard.getIndex());
                        sampleRequest.setNode2(smallShard.getNode());
                        sampleRequest.setShard2(smallShard.getShard());
                        smallSizedShards.getShards().remove(j);
                        resp.getClusterReroutePayloads().add(sampleRequest);
                        break;
                    }
                }
            }
        }
        return resp;
    }
```

EsUtil
```
public class EsUtil {

  public static final String TIMESTAMP_PATTERN = "yyyy-MM-dd'T'HH:mm:ss.nnnnnnZ";

  // 2022-03-10T10:45:50.000000-0700
  public static ZonedDateTime parseEsTimestampString(String timestampString) {
    ZonedDateTime timestamp = null;
    try {
      DateTimeFormatter fmt = DateTimeFormatter.ofPattern(TIMESTAMP_PATTERN);
      timestamp = ZonedDateTime.parse(timestampString, fmt);
    } catch (Exception e) {
      log.error("Invalid esTimestamp: " + timestampString);
    }
    return timestamp;
  }

  public static long toEsTimestampString(ZonedDateTime zonedDateTime) {
    return zonedDateTime.toInstant().toEpochMilli();
  }

  public static String getIndexFullName(
          String indexPrefix, ZonedDateTime zonedDateTime, String indexDateTimePattern, ZoneId zoneId) {

    DateTimeFormatter formatter = DateTimeFormatter.ofPattern(indexDateTimePattern);
    String indexTimePattern = zonedDateTime.withZoneSameInstant(zoneId).format(formatter);
    return indexPrefix + '_' + indexTimePattern;
  }


  public static String extractDateString(String input) {
    String pattern1 = "\\d{8}";
    String pattern2 = "(\\d{4}(?:[-_.]\\d{2}(?:[-_.]\\d{2})?)?)";

    Pattern regex1 = Pattern.compile(pattern1);
    Matcher matcher1 = regex1.matcher(input);

    if (matcher1.find()) {
      return matcher1.group();
    } else {
      Pattern regex2 = Pattern.compile(pattern2);
      Matcher matcher2 = regex2.matcher(input);

      if (matcher2.find()) {
        return matcher2.group(1);
      } else {
        return "";
      }
    }
  }

  public static boolean isCurrentDate(String dateString) {
    if (dateString.length() == 8 && StringUtils.isNumeric(dateString)) {
      StringBuilder dateStrBuilder = new StringBuilder(dateString);
      dateStrBuilder.insert(4, "-");
      dateStrBuilder.insert(7, "-");
      dateString = dateStrBuilder.toString();
    }

    String[] dateParts = dateString.split("[-_.]");

    LocalDate currentDate = LocalDate.now();

    if (dateParts.length == 1) { // YYYY
      int year = Integer.parseInt(dateParts[0]);
      return year == currentDate.getYear();
    } else if (dateParts.length == 2) { // YYYY-MM
      int year = Integer.parseInt(dateParts[0]);
      int month = Integer.parseInt(dateParts[1]);
      return year == currentDate.getYear() && month == currentDate.getMonthValue();
    } else if (dateParts.length == 3) { // YYYY-MM-DD
      int year = Integer.parseInt(dateParts[0]);
      int month = Integer.parseInt(dateParts[1]);
      int day = Integer.parseInt(dateParts[2]);
      return year == currentDate.getYear() && month == currentDate.getMonthValue() && day == currentDate.getDayOfMonth();
    } else if (dateParts.length == 1 && dateParts[0].length() == 8) { // YYYYMMDD
      DateTimeFormatter formatter = DateTimeFormatter.ofPattern("yyyyMMdd");
      LocalDate date = LocalDate.parse(dateParts[0], formatter);
      return date.isEqual(currentDate);
    }
    return false;
  }

  public static Predicate<Shard> createPredicate(String value, Function<Shard, String> fieldAccessor) {
    return shard -> {
      String fieldValue = fieldAccessor.apply(shard);

      if (fieldValue == null) {
        return false;
      }

      if (Util.startsWithWildCard(value)) {
        String suffix = value.substring(1);
        return fieldValue.endsWith(suffix);
      }

      if (Util.endsWithWildCard(value)) {
        String prefix = value.substring(0, value.length() - 1);
        return fieldValue.startsWith(prefix);
      }

      if ("b".equals(value)) {
        return fieldValue.endsWith(value) && !Character.isLetter(fieldValue.charAt(fieldValue.length() - 2));
      }

      if (value.matches("[kmg]b")) {
        return fieldValue.endsWith(value);
      }

      return fieldValue.equals(value);
    };
  }

  public static Map<String, List<Index>> groupIndicesByPrefix(List<Index> indices) {
    Map<String, List<Index>> groupedIndices = new HashMap<>();

    for (Index index : indices) {
      String indexName = index.getIndex();
      List<String> nameAndDate = splitPrefixAndDate(indexName);
      String prefix = nameAndDate.get(0);
      groupedIndices.computeIfAbsent(prefix, k -> new ArrayList<>()).add(index);
    }

    return groupedIndices;
  }

  public static Map<String, List<Index>> filterIndices(Map<String, List<Index>> groupedIndices,
                                                       List<Predicate<Map.Entry<String, List<Index>>>> predicates) {
    return groupedIndices.entrySet()
            .stream()
            .filter(entry -> predicates.stream().allMatch(p -> p.test(entry)))
            .collect(HashMap::new, (m, e) -> m.put(e.getKey(), e.getValue()), HashMap::putAll);
  }

  public static List<String> splitPrefixAndDate(String indexName) {
    List<String> res = new ArrayList<>();
    Pattern pattern = Pattern.compile("^(.*?[_-]?)(\\d{8}|\\d{6}|\\d{4}.*)$");
    Matcher matcher = pattern.matcher(indexName);

    if (matcher.find()) {
      res.add(matcher.group(1)); // captures before YYYYMMDD, YYYYMM, or YYYY excluding
      res.add(matcher.group(2)); // captures after YYYYMMDD, YYYYMM, or YYYY including
      return res;
    }
    res.add(indexName);
    return res;
  }

  public static Map<String, List<Index>> removeExtraSuffixTimePeriod(List<Index> indices) {
    if (indices.isEmpty()) {
      return new HashMap<>();
    }

    int charactersToRemove = 0;
    String convertedIndexName;

    String firstIndex = indices.get(0).getIndex();

    if (firstIndex.matches(".*\\d{8}$")                                // YYYYMMDD
      || firstIndex.matches(".*\\d{6}$")) {                            // YYYYMM
      charactersToRemove = 2;
    } else if (firstIndex.matches(".*\\d{4}[._-]\\d{2}[._-]\\d{2}.*") // YYYY-MM-DD
            || firstIndex.matches(".*\\d{4}[._-]\\d{2}.*")) {         // YYYY-MM
      charactersToRemove = 3;
    } else {
      return new HashMap<>();
    }

    Map<String, List<Index>> prefixToIndexList = new HashMap<>();
    if (charactersToRemove > 0) {
      for (Index index: indices) {
        String indexName = index.getIndex();
        convertedIndexName = indexName.substring(0, indexName.length() - charactersToRemove);
        prefixToIndexList.putIfAbsent(convertedIndexName, new ArrayList<>());
        prefixToIndexList.get(convertedIndexName).add(index);
      }
    }

    return prefixToIndexList;
  }

  public static Map<String, Map<String, List<Index>>> buildNestedIndexGroup(Map<String, List<Index>> prefixToFull) {
    Map<String, Map<String, List<Index>>> nestedMap = new HashMap<>();
    for (Map.Entry<String, List<Index>> entry: prefixToFull.entrySet()) {
      String prefix = entry.getKey();
      List<Index> indicesPerPrefix = entry.getValue();
      Map<String, List<Index>> modifiedPrefixToIndex = removeExtraSuffixTimePeriod(indicesPerPrefix);
      if (modifiedPrefixToIndex.isEmpty()) {
        continue;
      }
      nestedMap.put(prefix, modifiedPrefixToIndex);
    }
    return nestedMap;
  }
}
```
