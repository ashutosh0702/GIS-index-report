FROM public.ecr.aws/lambda/python:3.10

COPY src/lambda_function.py ${LAMBDA_TASK_ROOT}
COPY src/requirements.txt ${LAMBD_TASK_ROOT}

RUN pip install --no-cache-dir -r requirements.txt

CMD ["lambda_function.handler"]
