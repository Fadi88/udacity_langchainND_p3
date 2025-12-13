from langchain_core.tools import tool
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from data.models.cultpass import User, Subscription, Reservation, Experience
import json

# Setup DB connection
# In a real app, this would be dependency injected or from a singleton config
CP_DB_PATH = "sqlite:///cultpass.db"
engine = create_engine(CP_DB_PATH)
Session = sessionmaker(bind=engine)


@tool
def lookup_user(email: str) -> str:
    """
    Search for a user by email.
    Returns JSON string with user details or error message.
    """
    session = Session()
    try:
        user = session.query(User).filter(User.email == email).first()
        if user:
            return json.dumps(
                {
                    "user_id": user.user_id,
                    "full_name": user.full_name,
                    "email": user.email,
                    "is_blocked": user.is_blocked,
                }
            )
        return json.dumps({"error": "User not found"})
    except Exception as e:
        return json.dumps({"error": str(e)})
    finally:
        session.close()


@tool
def get_subscription_status(user_id: str) -> str:
    """
    Get subscription details for a user given their user_id.
    """
    session = Session()
    try:
        sub = (
            session.query(Subscription).filter(Subscription.user_id == user_id).first()
        )
        if sub:
            return json.dumps(
                {
                    "status": sub.status,
                    "tier": sub.tier,
                    "monthly_quota": sub.monthly_quota,
                    "expires_at": str(sub.ended_at) if sub.ended_at else "Auto-renew",
                }
            )
        return json.dumps({"error": "No subscription found"})
    except Exception as e:
        return json.dumps({"error": str(e)})
    finally:
        session.close()


@tool
def get_user_reservations(user_id: str) -> str:
    """
    List all reservations for a user given their user_id.
    """
    session = Session()
    try:
        reservations = (
            session.query(Reservation).filter(Reservation.user_id == user_id).all()
        )
        results = []
        for res in reservations:
            # Join with experience for details
            exp = (
                session.query(Experience)
                .filter(Experience.experience_id == res.experience_id)
                .first()
            )
            results.append(
                {
                    "reservation_id": res.reservation_id,
                    "status": res.status,
                    "class": exp.title if exp else "Unknown",
                    "when": str(exp.when) if exp else "Unknown",
                }
            )
        if not results:
            return json.dumps({"message": "No reservations found"})
        return json.dumps(results)
    except Exception as e:
        return json.dumps({"error": str(e)})
    finally:
        session.close()


@tool
def cancel_reservation(reservation_id: str) -> str:
    """
    Cancel a reservation given its reservation_id.
    """
    session = Session()
    try:
        res = (
            session.query(Reservation)
            .filter(Reservation.reservation_id == reservation_id)
            .first()
        )
        if res:
            res.status = "cancelled"
            session.commit()
            return json.dumps(
                {
                    "status": "success",
                    "message": f"Reservation {reservation_id} cancelled.",
                }
            )
        return json.dumps({"error": "Reservation not found"})
    except Exception as e:
        session.rollback()
        return json.dumps({"error": str(e)})
    finally:
        session.close()


@tool
def update_subscription(user_id: str, new_tier: str) -> str:
    """
    Update a user's subscription tier (e.g., 'basic' or 'elite').
    """
    session = Session()
    try:
        sub = (
            session.query(Subscription).filter(Subscription.user_id == user_id).first()
        )
        if sub:
            old_tier = sub.tier
            sub.tier = new_tier
            # Simple logic: Upgrade gives more quota, Downgrade reduces it
            if new_tier == "elite":
                sub.monthly_quota = 20
            else:
                sub.monthly_quota = 5

            session.commit()
            return json.dumps(
                {
                    "status": "success",
                    "message": f"Upgraded from {old_tier} to {new_tier}. Quota updated to {sub.monthly_quota}.",
                }
            )
        return json.dumps({"error": "Subscription not found"})
    except Exception as e:
        session.rollback()
        return json.dumps({"error": str(e)})
    finally:
        session.close()


import uuid


@tool
def book_reservation(user_id: str, experience_id: str) -> str:
    """
    Book a class/experience for a user.
    """
    session = Session()
    try:
        # Check if experience exists and has slots
        exp = (
            session.query(Experience)
            .filter(Experience.experience_id == experience_id)
            .first()
        )
        if not exp:
            return json.dumps({"error": "Experience not found"})

        if exp.slots_available < 1:
            return json.dumps({"error": "Class is full"})

        # Check if user already booked
        existing = (
            session.query(Reservation)
            .filter(
                Reservation.user_id == user_id,
                Reservation.experience_id == experience_id,
            )
            .first()
        )

        if existing and existing.status != "cancelled":
            return json.dumps({"error": "User already booked this class"})

        # Book it
        # Note: In production we'd handle race conditions and subscription quota decrement
        # Simplified for this project
        new_res_id = f"res-{uuid.uuid4().hex[:6]}"
        res = Reservation(
            reservation_id=new_res_id,
            user_id=user_id,
            experience_id=experience_id,
            status="confirmed",
        )
        exp.slots_available -= 1

        session.add(res)
        session.commit()
        return json.dumps(
            {
                "status": "success",
                "reservation_id": new_res_id,
                "message": f"Successfully booked {exp.title}.",
            }
        )
    except Exception as e:
        session.rollback()
        return json.dumps({"error": str(e)})
    finally:
        session.close()


@tool
def get_retention_policy() -> str:
    """
    Get the current retention policy and offers.
    """
    # In a real app, this might come from a CMS or DB
    policy = {
        "cancellation_fee": "None if cancelled 24h before renewal.",
        "pause_option": "Can pause for up to 3 months. Data is preserved.",
        "retention_offer": "10% discount for the next 3 months if they stay.",
        "refund_policy": "No refunds for partial months. Strictly no refunds for used passes.",
    }
    return json.dumps(policy)
