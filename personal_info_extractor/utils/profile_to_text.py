from schema.personal_profile import PersonalProfile

def convert_profile_to_embeddable_text(profile: PersonalProfile) -> str:

    if not profile:
        return ""

    parts = []

    if profile.name:
        parts.append(f"Name: {profile.name}.")
    if profile.age:
        parts.append(f"Age: {profile.age} years old.")
    if profile.location:
        parts.append(f"Location: {profile.location}.")
    if profile.education and profile.education.value:
        parts.append(f"Education: {profile.education.value}. Sentiment: {profile.education.sentiment if profile.education.sentiment else 'N/A'}. Confidence: {profile.education.confidence if profile.education.confidence is not None else 'N/A'}.")
    if profile.work_experience and profile.work_experience.values:
        parts.append(f"Work Experience: {', '.join(profile.work_experience.values)}. Sentiment: {profile.work_experience.sentiment if profile.work_experience.sentiment else 'N/A'}. Confidence: {profile.work_experience.confidence if profile.work_experience.confidence is not None else 'N/A'}.")
    if profile.interests and profile.interests.values:
        parts.append(f"Interests: {', '.join(profile.interests.values)}. Sentiment: {profile.interests.sentiment if profile.interests.sentiment else 'N/A'}. Confidence: {profile.interests.confidence if profile.interests.confidence is not None else 'N/A'}.")
    if profile.personality_traits:
        parts.append(f"Personality: {', '.join(profile.personality_traits)}.")
    if profile.skills and profile.skills.values:
        parts.append(f"Skills: {', '.join(profile.skills.values)}. Sentiment: {profile.skills.sentiment if profile.skills.sentiment else 'N/A'}. Confidence: {profile.skills.confidence if profile.skills.confidence is not None else 'N/A'}.")
    if profile.languages_spoken and profile.languages_spoken.values:
        parts.append(f"Languages: {', '.join(profile.languages_spoken.values)}. Sentiment: {profile.languages_spoken.sentiment if profile.languages_spoken.sentiment else 'N/A'}. Confidence: {profile.languages_spoken.confidence if profile.languages_spoken.confidence is not None else 'N/A'}.")
    if profile.achievements and profile.achievements.values:
        parts.append(f"Achievements: {', '.join(profile.achievements.values)}. Sentiment: {profile.achievements.sentiment if profile.achievements.sentiment else 'N/A'}. Confidence: {profile.achievements.confidence if profile.achievements.confidence is not None else 'N/A'}.")
    if profile.contact_info:
        parts.append(f"Contact Info: {', '.join(profile.contact_info)}.")

    return " ".join(parts)
