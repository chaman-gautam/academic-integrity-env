# """FastAPI server to expose the OpenEnv environment via HTTP endpoints."""
# from fastapi import FastAPI, HTTPException
# from pydantic import BaseModel
# from environment import AcademicIntegrityEnv
# from models import InvestigationObservation, InvestigationAction, InvestigationState

# app = FastAPI(title="Academic Integrity Investigation Environment")
# env = AcademicIntegrityEnv()

# class ResetRequest(BaseModel):
#     task: str = "easy"

# class StepRequest(BaseModel):
#     action: InvestigationAction

# class StepResponse(BaseModel):
#     observation: InvestigationObservation
#     reward: float
#     done: bool
#     info: dict

# @app.post("/reset")
# async def reset_endpoint(req: ResetRequest):
#     obs = env.reset(req.task)
#     return {"observation": obs.dict()}

# @app.post("/step")
# async def step_endpoint(req: StepRequest):
#     try:
#         obs, reward, done, info = env.step(req.action)
#         return StepResponse(observation=obs, reward=reward, done=done, info=info)
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=str(e))

# @app.get("/state")
# async def state_endpoint():
#     state = env.state()
#     return state.dict()

# @app.get("/openenv.yaml")
# async def get_openenv_yaml():
#     from fastapi.responses import FileResponse
#     return FileResponse("openenv.yaml", media_type="text/yaml")

# @app.on_event("shutdown")
# async def shutdown():
#     env.close()