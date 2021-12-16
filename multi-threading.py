import random
from threading import Thread
import time
import traceback


class SafeThread(Thread):
	"""SafeThread.
	
	A custom thread implementation that allows raising exception
	to the caller thread.
	"""
	def __init__(self, *args, **kwargs):
		"""init."""
		super(SafeThread, self).__init__(*args, **kwargs)
		self.exception = None

	def run(self) -> None:
		"""run."""
		try:
			super(SafeThread, self).run()
		except Exception as ex:
			self.exception = ex

	def join(self, *args, **kwargs) -> None:
		"""join."""
		super(SafeThread, self).join(*args, **kwargs)
		if self.exception:
			raise self.exception


def step1_validation(*args, **kwargs):
	"""step1_validation.
	
	This validation does some DB operation, the operation
	would happen parallely along with other threads as its
	an io operation, there is no gurantee
	when it will complete
	"""
	operation_time = random.randrange(5)
	time.sleep(operation_time)
	# random time sleep to stimulate db call
	if kwargs.get("fail_test") == "step1_validation":
		raise Exception(f"Step 1 validation failed in {operation_time} seconds")
	print(f"step 1 validation completed in {operation_time} seconds")


def step2_validation(*args, **kwargs):
	"""step2_validation.

	This validation does some External API call, the call
	would happen parallely along with other threads as its
	an wait operation not a code execution, there is no gurantee
	when it will complete
	"""
	operation_time = random.randrange(5)
	time.sleep(operation_time)
	# random time sleep to stimulate external api call
	if kwargs.get("fail_test") == "step2_validation":
		raise Exception(f"Step 2 validation failed in {operation_time} seconds")
	print(f"step 2 validation completed in {operation_time} seconds")


def step3_validation(*args, **kwargs):
	"""step3_validation.
	
	This validation does some basic code level check, the check
	would not happen parallely along with other threads as its
	not a wait operation its a pure code execution. so if other
	validation don't have any io operation, step3 will be last
	else it will be 1st or 2nd to complete
	"""
	if kwargs.get("fail_test") == "step3_validation":
		raise Exception("Step 3 validation failed without delay")
	print("step 3 validation completed without delay")


def step4_process(*args, **kwargs):
	"""step4_process."""
	print("step4_process completed")


def step5_process(*args, **kwargs):
	"""step5_process."""
	print("step5_process completed")


def step6_process(*args, **kwargs):
	"""step6_process."""
	print("step6_process completed")


def main_api_handler(*args, **kwargs):
	"""main_api_handler.
	
	accepts fail_test keyword which has name of validation
	function which should fail. 
	this handler will be called from the main api post method
	"""
	try:
		# creating threads for validations
		validation1 = SafeThread(target=step1_validation, args=args, kwargs=kwargs)
		validation2 = SafeThread(target=step2_validation, args=args, kwargs=kwargs)
		validation3 = SafeThread(target=step3_validation, args=args, kwargs=kwargs)

		# starting validations concurrently
		validation1.start()
		validation2.start()
		validation3.start()

		# waiting for validation threads to conclude before moving ahead
		validation1.join()
		validation2.join()
		validation3.join()

		step4_process(*args, **kwargs)
		process5 = SafeThread(target=step5_process, args=args, kwargs=kwargs)
		process6 = SafeThread(target=step6_process, args=args, kwargs=kwargs)

		process5.start()
		process6.start()
		process5.join()
		process6.join()
		return {"success": True, "message": "Api call was completed succesfully"}
	except Exception as e:
		return {"success": False, "message": str(e)}
