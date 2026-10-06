Credenciais de Autenticação Capturadas
Risco: Alto
An insecure authentication mechanism is in use. This allows an attacker on the network access to the userid and password of the authenticated user. For Basic Authentication, the attacker must merely monitor the network traffic until a Basic Authentication request is received, and then base64 decode the username and password. For Digest Authentication, the attacker has access to the username, and possibly also the password, if the hash (including a nonce) can be successfully cracked, or if a Man-In-The-Middle attack is mounted.
The attacker eavesdrops on the network until an authentication has completed.
[POST] [http://127.0.0.1:8000/auth/token] uso de mecanismo inseguro de autenticação [Basic], revelando o nome de usuário [] e a senha [].

Conclusão: Falso positivo. O ZAP identificou o envio de credenciais pelo endpoint /auth/token devido à utilização de HTTP sem TLS. A aplicação utiliza OAuth2 Password Flow para autenticação e JWT para autorização, porém o ambiente local não utiliza HTTPS. Em ambiente de produção, a API deve ser disponibilizada exclusivamente sobre HTTPS para impedir a interceptação das credenciais e dos tokens.


CSP: Failure to Define Directive with No Fallback
Risco: Médio
The Content Security Policy fails to define one of the directives that has no fallback. Missing/excluding them is the same as allowing anything.

Conclusão: Alerta válido. response.headers["Content-Security-Policy"] atualizado.


CSP: script-src unsafe-inline
Risco: Médio
Content Security Policy (CSP) is an added layer of security that helps to detect and mitigate certain types of attacks. Including (but not limited to) Cross Site Scripting (XSS), and data injection attacks. These attacks are used for everything from data theft to site defacement or distribution of malware. CSP provides a set of standard HTTP headers that allow website owners to declare approved sources of content that browsers should be allowed to load on that page — covered types are JavaScript, CSS, HTML frames, fonts, images and embeddable objects such as Java applets, ActiveX, audio and video files.

Conclusão: Alerta válido, porem a flag é necessária para rodar o docs. Não estará em produção.


CSP: style-src unsafe-inline
Risco: Médio
Content Security Policy (CSP) is an added layer of security that helps to detect and mitigate certain types of attacks. Including (but not limited to) Cross Site Scripting (XSS), and data injection attacks. These attacks are used for everything from data theft to site defacement or distribution of malware. CSP provides a set of standard HTTP headers that allow website owners to declare approved sources of content that browsers should be allowed to load on that page — covered types are JavaScript, CSS, HTML frames, fonts, images and embeddable objects such as Java applets, ActiveX, audio and video files.

Conclusão: Idem.


Configuração Incorreta Entre Domínios
Risco: Médio
Web browser data loading may be possible, due to a Cross Origin Resource Sharing (CORS) misconfiguration on the web server.

Conclusão: Alerta válido. Isso se deve pelo allow_credentials=True. Como não temos front-end ainda, a solução é deixar allow_origins=[]

Conclusão: Alerta válido, é causado por arquivos JavaScript utilizados pela interface Swagger UI, carregados a partir do CDN jsDelivr sem atributo integrity. A API não utiliza esses recursos externos em seus endpoints de negócio. Para produção, recomenda-se hospedar os recursos localmente ou utilizar Subresource Integrity para validar os arquivos externos.