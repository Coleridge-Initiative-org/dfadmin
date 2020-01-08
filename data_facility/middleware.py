import http.cookies

class CookieIntercept(object):
    def process_response(self, request, response):
        if response.cookies.has_key('csrftoken'):
            csrftoken = response.cookies['csrftoken']

            c_value = csrftoken.value
            lambdaFunction = "csrftoken=" + c_value

            c_expires = csrftoken['expires']
            if c_expires:
                lambdaFunction += "; expires=" + c_expires
            
            c_path = csrftoken['path']
            if c_path:
                lambdaFunction += "; Path=" + c_path

            c_maxAge = csrftoken['max-age']
            if c_maxAge:
                lambdaFunction += "; Max-Age=" + str(c_maxAge)

            c_httpOnly = csrftoken['httponly']
            if c_httpOnly:
                lambdaFunction += "; httponly"

            c_secure = csrftoken['secure']
            if c_secure:
                lambdaFunction += "; secure"
            
            c_version = csrftoken['version']
            if c_version:
                lambdaFunction += "; version=" + str(c_version)
                        
            c_domain = csrftoken['domain']
            if c_domain:
                lambdaFunction += "; domain=" + str(c_domain)
            
            comment = csrftoken['comment']
            if comment:
                lambdaFunction += "; comment=" + str(comment)

            lambdaFunction += "; samesite=Strict"

            csrftoken.output = lambda attrs=None, header="Set-Cookie:": lambdaFunction

        return response