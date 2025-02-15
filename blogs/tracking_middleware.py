# import datetime
# from django.utils.timezone import now
# from django.utils.deprecation import MiddlewareMixin
# from .models import PageVisit

# class PageVisitMiddleware(MiddlewareMixin):
#     def process_request(self, request):
#         """Log the start of a page visit"""
#         ip_address = self.get_client_ip(request)
#         user = request.user if request.user.is_authenticated else None
#         session_key = request.session.session_key

#         if not session_key:
#             request.session.create()
#             session_key = request.session.session_key

#         request.page_visit = PageVisit.objects.create(
#             user=user,
#             session_key=session_key if not user else None,  # Track session key if user is anonymous
#             ip_address=ip_address,
#             url=request.path,
#             user_agent=request.META.get('HTTP_USER_AGENT', ''),
#             referrer=request.META.get('HTTP_REFERER', '')
#         )

#     def process_response(self, request, response):
#         """Log the end time of a page visit"""
#         if hasattr(request, 'page_visit'):
#             request.page_visit.end_time = now()
#             request.page_visit.save()
#         return response

#     def get_client_ip(self, request):
#         """Extract the real IP address from the request"""
#         x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
#         if x_forwarded_for:
#             ip = x_forwarded_for.split(',')[0]
#         else:
#             ip = request.META.get('REMOTE_ADDR')
#         return ip
