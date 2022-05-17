# AutoSpear
We will release the source code of AutoSpear after all vendors complete the fix process.

# Statement
I have noted in the presentation slides that the four WAFs (AWS, Fortinet, F5, and CSC) are deployed based on AWS ACLs and the managed rulesets (https://aws.amazon.com/marketplace/solutions/security/waf-managed-rules) provided by these vendors. 
Here I may restress that the three WAFs (Fortinet, F5, and CSC) under test in this configuration are not precisely the same as the independent WAFs provided by the vendors on their official websites.

Specifically:
(1) Amazon Web Services (AWS). We create a load balancer on AWS and add an Access Control List (ACL) to it. On this ACL, we select two AWS-managed rule groups related to SQLi, e.g., `Core ruleset` and `SQL database`.<br>
(2) F5. AWS allows users to add third-party vendors provided rule sets in the marketplace to the ACL. We replace the AWS rules in (1) with `F5 Web Exploits OWASP Rules`.<br>
(3) Cyber Security Cloud (CSC). Similar to (2), we subscribe to the `Cyber Security Cloud Managed Rules for AWS WAF - HighSecurity OWASP Set` and add it to ACL.<br>
(4) Fortinet. Fortinet also provides their ruleset `Fortinet OWASP Top 10 - The Complete Ruleset` in the AWS marketplace, which is a comprehensive package to help address threats as described in OWASP Top 10.<br>
(5) Cloudflare. Cloudflare's free version does not allow users to use managed rules. Therefore, we subscribe to Cloudflare's pro plan to enable the full-blown WAF. We turn on the three rule sets: `Cloudflare Specials`, `OWASP Common Exceptions` and `OWASP Generic Attack` to defend against SQLi attacks.<br>
(6) Wallarm. Wallarm applies machine learning to adaptively generate security rules and verifies the impact of malicious payloads in real-time. We deploy a Wallarm Node (for trial) based on Google Cloud Platform to enable its WAF function.<br>
(7) ModSecurity. We build and deploy ModSecurity based on Nginx and embed the latest version of the OWASP Core Rule Set (CRS) in it. Besides, we set the Paranoia Level of CRS as the default, i.e., PL1.<br>

Besides, I must reiterate that our provided results and rankings of vendors are obtained with our limited settings and dataset samples, which cannot fully represent the actual defense effects against all samples in the wild.
