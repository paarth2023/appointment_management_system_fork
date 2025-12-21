# from rest_framework.views import APIView
# from rest_framework.permissions import IsAuthenticated
# from rest_framework.response import Response

# from .llm import run_llm
# from .executor import execute_action

# class AgentExecuteView(APIView):
#     permission_classes = [IsAuthenticated]

#     def post(self, request):
#         user_message = request.data.get("message", "").strip()
#         context = request.data.get("context", {}) or {}

#         llm_output = run_llm(user_message, context)

#         if "message" in llm_output:
#             return Response({
#                 "type": "question",
#                 "message": llm_output["message"],
#                 "context": context
#             })

#         result = execute_action(
#             llm_output["action"],
#             llm_output["params"],
#             request
#         )

#         new_context = context.copy()
#         new_context.update(result.get("context", {}))

#         return Response({
#             "type": "result",
#             "action": llm_output["action"],
#             "data": result["data"],
#             "context": new_context
#         })

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .llm import run_llm
from .executor import execute_action
from .formatter import format_response_with_llm


class AgentExecuteView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user_message = request.data.get("message", "").strip()
        context = request.data.get("context", {}) or {}

        llm_output = run_llm(user_message, context)

        if "message" in llm_output:
            return Response(
                {
                    "type": "question",
                    "message": llm_output["message"],
                    "context": context,
                }
            )

        result = execute_action(llm_output["action"], llm_output["params"], request)

        new_context = context.copy()
        new_context.update(result.get("context", {}))

        # Format the response using LLM for better presentation
        formatted_message = format_response_with_llm(
            llm_output["action"], result["data"], user_message
        )

        return Response(
            {
                "type": "result",
                "action": llm_output["action"],
                "data": result["data"],
                "formatted_message": formatted_message,  # Add formatted message
                "context": new_context,
            }
        )
