from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.dependencies import get_current_user
from app.core.response import success_response
from app.models.user import User
from app.models.emergency_contact import EmergencyContact
from app.schemas.emergency_contact import EmergencyContactCreate, EmergencyContactUpdate, EmergencyContactResponse

router = APIRouter(prefix="/emergency-contacts", tags=["Emergency Contacts"])

@router.get("", summary="List User's Emergency Contacts")
def list_contacts(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    contacts = db.query(EmergencyContact).filter(EmergencyContact.user_id == current_user.id).all()
    return success_response(
        data=[EmergencyContactResponse.model_validate(c) for c in contacts],
        message="Emergency contacts retrieved"
    )

@router.post("", summary="Create Emergency Contact")
def create_contact(
    contact_data: EmergencyContactCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # check max 5
    count = db.query(EmergencyContact).filter(EmergencyContact.user_id == current_user.id).count()
    if count >= 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum of 5 emergency contacts allowed"
        )
    
    contact = EmergencyContact(
        user_id=current_user.id,
        name=contact_data.name,
        phone=contact_data.phone,
        relation=contact_data.relation
    )
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return success_response(
        data=EmergencyContactResponse.model_validate(contact),
        message="Emergency contact created successfully"
    )

@router.patch("/{contact_id}", summary="Update Emergency Contact")
def update_contact(
    contact_id: str,
    update_data: EmergencyContactUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    contact = db.query(EmergencyContact).filter(EmergencyContact.id == contact_id, EmergencyContact.user_id == current_user.id).first()
    if not contact:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Emergency contact not found")
    
    if update_data.name is not None:
        contact.name = update_data.name
    if update_data.phone is not None:
        contact.phone = update_data.phone
    if update_data.relation is not None:
        contact.relation = update_data.relation
    
    db.commit()
    db.refresh(contact)
    return success_response(
        data=EmergencyContactResponse.model_validate(contact),
        message="Emergency contact updated successfully"
    )

@router.delete("/{contact_id}", summary="Delete Emergency Contact")
def delete_contact(
    contact_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    contact = db.query(EmergencyContact).filter(EmergencyContact.id == contact_id, EmergencyContact.user_id == current_user.id).first()
    if not contact:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Emergency contact not found")
    
    db.delete(contact)
    db.commit()
    return success_response(data=None, message="Emergency contact deleted successfully")
