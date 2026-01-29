from sqlalchemy.orm import Session
from app.models.models import User, UserStageEnum, University, RankTier, Shortlist
from app.schemas.ai import AIResponse, AIAction

class AIService:
    @staticmethod
    def reason(user: User, db: Session) -> AIResponse:
        stage = user.stage.current_stage
        profile = user.profile

        # --- PROFILE STAGE ---
        if stage == UserStageEnum.PROFILE:
            # Analyze Strength
            if not profile.profile_completed:
                return AIResponse(
                    message="Your profile is incomplete. Please finish onboarding to enable my services.",
                    actions=[],
                    next_suggestion="Complete Onboarding"
                )
            
            # Check Academics
            gpa_ok = profile.gpa and profile.gpa >= 3.0
            
            # Check Exams
            exams_started = (
                profile.ielts_status in ["Planned", "Taken", "Prepared", "In Progress"] or 
                profile.gre_status in ["Planned", "Taken", "Prepared", "In Progress"]
            )

            if gpa_ok:
                if exams_started:
                    msg = "Your academic and exam profile looks solid. You are ready to start exploring universities!"
                else:
                    msg = "Your academics are strong, but you still need to work on your Exams (IELTS/GRE). You can start exploring universities while you prepare."

                return AIResponse(
                    message=msg,
                    actions=[
                        AIAction(
                            type="TRANSITION", 
                            label="Start Discovery Phase", 
                            payload={"target_stage": "DISCOVERY"}
                        )
                    ],
                    next_suggestion="Move to Discovery"
                )
            else:
                return AIResponse(
                    message="Your GPA is on the lower side. I recommend focusing on strong SOPs or improving test scores before discovery.",
                    actions=[], # No transition yet
                    next_suggestion="Improve Profile"
                )

        # --- DISCOVERY STAGE ---
        elif stage == UserStageEnum.DISCOVERY:
            # Check shortlists
            shortlist_count = db.query(Shortlist).filter(Shortlist.user_id == user.id).count()
            
            if shortlist_count >= 1:
                return AIResponse(
                    message=f"You have shortlisted {shortlist_count} universities. Are you ready to finalize your choices?",
                    actions=[
                        AIAction(type="TRANSITION", label="Move to Finalize Phase", payload={"target_stage": "FINALIZE"})
                    ],
                    next_suggestion="Finalize Choices"
                )
            
            # Recommend based on budget/country
            # Dummy Logic: Find max 3 unis matching country
            
            target_countries = profile.preferred_countries or []
            
            query = db.query(University)
            if target_countries:
                # Basic filter - check if country in list
                all_unis = query.all()
                matches = [u for u in all_unis if u.country in target_countries]
            else:
                matches = query.limit(3).all()
            
            if not matches:
                # Fallback
                matches = db.query(University).limit(3).all()
            
            actions = []
            for uni in matches[:3]:
                actions.append(AIAction(
                    type="SHORTLIST",
                    label=f"Shortlist {uni.name} ({uni.country})",
                    payload={"university_id": uni.id}
                ))
            
            return AIResponse(
                message=f"Based on your preference for {', '.join(target_countries) if target_countries else 'anywhere'}, here are top recommendations:",
                actions=actions,
                next_suggestion="Shortlist 2-3 universities"
            )

        # --- FINALIZE STAGE ---
        elif stage == UserStageEnum.FINALIZE:
            # Analyze Shortlists
            shortlists = db.query(Shortlist).filter(Shortlist.user_id == user.id).all()
            locked_count = sum(1 for s in shortlists if s.locked)
            
            if locked_count == 0:
                 # Suggest Locking the best one (Dummy: first one)
                 if shortlists:
                     best = shortlists[0]
                     return AIResponse(
                        message="You need to commit to at least one university to proceed. I recommend starting with your top choice.",
                        actions=[
                            AIAction(type="LOCK", label=f"Lock {best.university.name}", payload={"university_id": best.university.id})
                        ],
                        next_suggestion="Lock a University"
                     )
                 else:
                     return AIResponse(message="No shortlists found.", actions=[], next_suggestion="Go back")

            else:
                return AIResponse(
                    message=f"Great! you have locked {locked_count} universities. You can now proceed to Application.",
                    actions=[
                        AIAction(type="TRANSITION", label="Start Application Phase", payload={"target_stage": "APPLICATION"}) # Should actually use separate endpoint, but let's keep consistent if transitioning via AI
                    ],
                    next_suggestion="Start Applications"
                 )

        # --- APPLICATION STAGE ---
        elif stage == UserStageEnum.APPLICATION:
            from app.models.models import Task, TaskStatus
            pending_count = db.query(Task).filter(
                Task.user_id == user.id, 
                Task.status == TaskStatus.PENDING
            ).count()
            
            if pending_count > 0:
                 return AIResponse(
                    message=f"You have {pending_count} pending application tasks. Keep pushing to meet your deadlines!",
                    actions=[],
                    next_suggestion="Complete Tasks"
                 )
            else:
                 return AIResponse(
                    message="All applications submitted! Now we wait for the results. Relax and prepare for potential interviews.",
                    actions=[],
                    next_suggestion="Wait for Decisions"
                 )

        return AIResponse(message="I am sleeping.", actions=[], next_suggestion="Wait")
