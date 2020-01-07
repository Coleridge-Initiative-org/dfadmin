class CookieIntercept(object):

    def process_response(self,request, response):
         if response.cookies.has_key('csrftoken' ):
                csrftoken = response.cookies['csrftoken']