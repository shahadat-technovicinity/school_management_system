from django.urls import path
from .views import (
    CharacterCertificateListCreateView,
    CharacterCertificateDetailView,
    CharacterCertificateStatusUpdateView,
    DownloadCharacterCertificatePDFView,
    MoveCharacterCertificateToNothiArchiveView,
)

urlpatterns = [
    # List and Create Applications
    path(
        'character-certificates/', 
        CharacterCertificateListCreateView.as_view(), 
        name='character-certificate-list-create'
    ),
    
    # Detail View (Retrieve, Update, Delete)
    path(
        'character-certificates/<int:pk>/', 
        CharacterCertificateDetailView.as_view(), 
        name='character-certificate-detail'
    ),
    
    # Status Update (Approve / Reject)
    path(
        'character-certificates/<int:pk>/status/', 
        CharacterCertificateStatusUpdateView.as_view(), 
        name='character-certificate-status-update'
    ),
    
    # Download Approved Certificate PDF
    path(
        'character-certificates/<int:pk>/download-pdf/', 
        DownloadCharacterCertificatePDFView.as_view(), 
        name='character-certificate-download-pdf'
    ),
    
    # Archive to Nothi
    path(
        'character-certificates/<int:pk>/move-to-nothi/', 
        MoveCharacterCertificateToNothiArchiveView.as_view(), 
        name='character-certificate-move-to-nothi'
    ),
]