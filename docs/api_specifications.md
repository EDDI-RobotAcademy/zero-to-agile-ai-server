# Public Data Portal API Specifications

## Overview
This document describes the specifications for Public Data Portal APIs used in the Risk Analysis module.

## 1. Building Ledger API (건축물대장 API)

### Purpose
Retrieve building registration information including violation status, seismic design, approval date, and structural information.

### Base Information
- **Service Provider**: Ministry of Land, Infrastructure and Transport (국토교통부)
- **Service Name**: BldRgstService_v2
- **Base URL**: `http://apis.data.go.kr/1613000/BldRgstService_v2`
- **Authentication**: API Key (Query Parameter)
- **Response Format**: XML

### Endpoints

#### 1.1 getBrRecapTitleInfo (건축물 표제부 조회)
Retrieves building title information.

**Endpoint**: `/getBrRecapTitleInfo`

**Method**: GET

**Parameters**:

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| serviceKey | String | Yes | API authentication key (encoded) | Your encoded API key |
| sigunguCd | String | Yes | 시군구 코드 (5 digits) | 11440 (Mapo-gu) |
| bjdongCd | String | Yes | 법정동 코드 (5 digits) | 10100 |
| bun | String | No | 번 (building number) | 0001 |
| ji | String | No | 지 (sub-number) | 0000 |
| numOfRows | Integer | No | Number of rows per page | 10 |
| pageNo | Integer | No | Page number | 1 |

**Response Fields** (Key fields for risk analysis):

| Field | Type | Description | Risk Analysis Usage |
|-------|------|-------------|---------------------|
| useAprDay | String | 사용승인일 (Approval date) | Building age calculation |
| vlRatEstmTotArea | Number | 위반 면적 (Violation area) | Violation risk check |
| etcStrct | String | 구조 (Structure type) | Structural analysis |
| heit | Number | 높이 (Height) | Building characteristics |
| strctCdNm | String | 구조코드명 | Structure type classification |

**Sample Request**:
```
GET http://apis.data.go.kr/1613000/BldRgstService_v2/getBrRecapTitleInfo?serviceKey={encoded_key}&sigunguCd=11440&bjdongCd=10100&bun=0001&ji=0000&numOfRows=10&pageNo=1
```

**Sample Response** (XML):
```xml
<response>
  <header>
    <resultCode>00</resultCode>
    <resultMsg>NORMAL SERVICE.</resultMsg>
  </header>
  <body>
    <items>
      <item>
        <platPlc>서울특별시 마포구 신정동 123-45</platPlc>
        <useAprDay>20200115</useAprDay>
        <vlRatEstmTotArea>0</vlRatEstmTotArea>
        <etcStrct>철근콘크리트구조</etcStrct>
        <heit>15.5</heit>
        <strctCdNm>철근콘크리트구조</strctCdNm>
      </item>
    </items>
    <numOfRows>10</numOfRows>
    <pageNo>1</pageNo>
    <totalCount>1</totalCount>
  </body>
</response>
```

**Error Codes**:

| Code | Message | Description |
|------|---------|-------------|
| 00 | NORMAL SERVICE | Success |
| 01 | APPLICATION ERROR | Application error |
| 02 | DB ERROR | Database error |
| 03 | NO DATA | No data found |
| 04 | HTTP ERROR | HTTP communication error |
| 05 | SERVICE TIME OUT | Service timeout |
| 10 | INVALID REQUEST PARAMETER ERROR | Invalid parameter |
| 11 | NO MANDATORY REQUEST PARAMETERS ERROR | Missing required parameter |
| 12 | NO OPENAPI SERVICE ERROR | Service not available |
| 20 | SERVICE ACCESS DENIED ERROR | Access denied (invalid key) |
| 22 | LIMITED NUMBER OF SERVICE REQUESTS EXCEEDS ERROR | Rate limit exceeded |

---

## 2. Real Transaction Price API (아파트 실거래가 API)

### Purpose
Retrieve actual transaction prices for apartments to calculate price deviation risk.

### Base Information
- **Service Provider**: Ministry of Land, Infrastructure and Transport (국토교통부)
- **Service Name**: RTMSOBJSvc (Real Transaction Management System Object Service)
- **Base URL**: `http://openapi.molit.go.kr:8081/OpenAPI_ToolInstallPackage/service/rest/RTMSOBJSvc`
- **Authentication**: API Key (Query Parameter)
- **Response Format**: XML

### Endpoints

#### 2.1 getRTMSDataSvcAptTradeDev (아파트 실거래 조회)
Retrieves apartment transaction data.

**Endpoint**: `/getRTMSDataSvcAptTradeDev`

**Method**: GET

**Parameters**:

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| serviceKey | String | Yes | API authentication key (encoded) | Your encoded API key |
| LAWD_CD | String | Yes | 지역코드 (5 digits) | 11440 (Mapo-gu) |
| DEAL_YMD | String | Yes | 거래년월 (YYYYMM) | 202312 |
| numOfRows | Integer | No | Number of rows per page | 100 |
| pageNo | Integer | No | Page number | 1 |

**Response Fields** (Key fields for risk analysis):

| Field | Type | Description | Risk Analysis Usage |
|-------|------|-------------|---------------------|
| dealAmount | String | 거래금액 (Transaction price) | Price deviation calculation |
| buildYear | String | 건축년도 (Build year) | Age calculation |
| dealYear | String | 거래년도 | Transaction date |
| dealMonth | String | 거래월 | Transaction date |
| dealDay | String | 거래일 | Transaction date |
| exclusiveArea | String | 전용면적 (Exclusive area) | Price per area calculation |
| dong | String | 법정동 (Legal dong) | Regional matching |
| aptNm | String | 아파트명 (Apartment name) | Property identification |

**Sample Request**:
```
GET http://openapi.molit.go.kr:8081/OpenAPI_ToolInstallPackage/service/rest/RTMSOBJSvc/getRTMSDataSvcAptTradeDev?serviceKey={encoded_key}&LAWD_CD=11440&DEAL_YMD=202312&numOfRows=100&pageNo=1
```

**Sample Response** (XML):
```xml
<response>
  <header>
    <resultCode>00</resultCode>
    <resultMsg>NORMAL SERVICE.</resultMsg>
  </header>
  <body>
    <items>
      <item>
        <dealAmount>70,000</dealAmount>
        <buildYear>2020</buildYear>
        <dealYear>2023</dealYear>
        <dealMonth>12</dealMonth>
        <dealDay>15</dealDay>
        <exclusiveArea>84.99</exclusiveArea>
        <dong>신정동</dong>
        <aptNm>마포자이</aptNm>
      </item>
    </items>
    <numOfRows>100</numOfRows>
    <pageNo>1</pageNo>
    <totalCount>245</totalCount>
  </body>
</response>
```

**Error Codes**: Same as Building Ledger API

---

## 3. Rate Limits and Best Practices

### Rate Limits
- **Public Data Portal**: Typically 1,000 requests/day per API key
- **Recommendation**: Implement exponential backoff for 429 errors
- **Cache Strategy**: Cache responses for at least 1 hour

### Error Handling Strategy
1. **Retry Logic**: Implement retry with exponential backoff (max 3 retries)
2. **Timeout**: Set timeout to 10 seconds per request
3. **Fallback**: Use cached data when API is unavailable
4. **Logging**: Log all API errors with request parameters

### Data Freshness
- **Building Ledger**: Updated monthly
- **Transaction Price**: Updated monthly (around 20th of each month)
- **Recommendation**: Refresh data weekly

---

## 4. Regional Codes (지역코드)

### Seoul (서울) Region Codes (LAWD_CD / sigunguCd)

| District | Code | Korean Name |
|----------|------|-------------|
| Mapo-gu | 11440 | 마포구 |
| Yongsan-gu | 11400 | 용산구 |
| Yeongdeungpo-gu | 11560 | 영등포구 |
| Seodaemun-gu | 11410 | 서대문구 |
| Eunpyeong-gu | 11380 | 은평구 |

### Legal Dong Codes (bjdongCd) - Mapo-gu Example

| Dong Name | Code | Korean Name |
|-----------|------|-------------|
| Yeonnam-dong | 10100 | 연남동 |
| Seogyo-dong | 10200 | 서교동 |
| Hapjeong-dong | 10300 | 합정동 |
| Daeheung-dong | 10400 | 대흥동 |
| Ahyeon-dong | 10500 | 아현동 |

**Note**: Complete legal dong code list can be obtained from the Administrative Standard Code Management System (행정표준코드관리시스템).

---

## 5. Implementation Notes

### XML Parsing
- Use `xml.etree.ElementTree` or `lxml` for parsing
- Handle encoding issues (response may be in EUC-KR)
- Validate response structure before accessing fields

### API Key Management
- Store in environment variables (never commit to repository)
- Use URL encoding for API keys in query parameters
- Rotate keys periodically

### Testing Strategy
- Use mocked responses for unit tests
- Create sample XML files for different scenarios
- Test error handling with various error codes

---

## 6. Future Enhancements (Phase 2+)

### Additional APIs to Consider
1. **전세가격 API**: Jeonse (long-term lease) price data
2. **토지대장 API**: Land registry information
3. **융자정보 API**: Mortgage information (if available)
4. **지역통계 API**: Regional statistics

### Advanced Features
- Bulk data collection
- Real-time data streaming
- Historical data analysis
- Predictive price modeling

---

## References

- [공공데이터포털](https://www.data.go.kr/)
- [건축물대장 API 상세](https://www.data.go.kr/data/15044713/openapi.do)
- [아파트 실거래가 API 상세](https://www.data.go.kr/data/15058017/openapi.do)
- [행정표준코드관리시스템](https://www.code.go.kr/)

---

**Last Updated**: 2024-12-22
**Version**: 1.0
**Author**: BE-2 (Risk Engineering Team)
