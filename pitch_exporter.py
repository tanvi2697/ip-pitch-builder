import os
import requests
from io import BytesIO
from datetime import datetime
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

def download_image(url):
    """Download image from URL and return as BytesIO object"""
    try:
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            return BytesIO(response.content)
        else:
            return None
    except Exception as e:
        print(f"Error downloading image: {e}")
        return None

def generate_pitch_pdf(
    title, 
    adaptation_type,
    pitch_content, 
    plot_synopsis,
    character_profiles, 
    poster_image_url=None,
    teaser_script=None, 
    market_analysis=None,
    cast_suggestions=None,
    output_path="pitch_deck.pdf"
):
    """
    Generate a PDF pitch deck based on the provided content
    
    Args:
        title (str): Project title
        adaptation_type (str): Type of adaptation (Movie, TV Series)
        pitch_content (dict): Pitch deck content with high concept, logline, etc.
        plot_synopsis (dict): Plot synopsis with short/detailed synopses and act structure
        character_profiles (list): List of character profile dicts
        poster_image_url (str): URL of the generated poster image
        teaser_script (dict): Teaser trailer script details
        market_analysis (str): Market analysis text
        cast_suggestions (str): Cast suggestions text
        output_path (str): Where to save the PDF
        
    Returns:
        str: Path to the generated PDF
    """
    
    # Create document
    doc = SimpleDocTemplate(output_path, pagesize=letter, 
                           rightMargin=72, leftMargin=72,
                           topMargin=72, bottomMargin=72)
    
    # Get styles
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='Title',
                             fontName='Helvetica-Bold',
                             fontSize=24,
                             alignment=1,
                             spaceAfter=12))
    
    styles.add(ParagraphStyle(name='Subtitle',
                             fontName='Helvetica-Bold',
                             fontSize=18,
                             alignment=1,
                             spaceAfter=12))
    
    styles.add(ParagraphStyle(name='Heading1',
                             fontName='Helvetica-Bold',
                             fontSize=16,
                             spaceAfter=10))
    
    styles.add(ParagraphStyle(name='Heading2',
                             fontName='Helvetica-Bold',
                             fontSize=14,
                             spaceAfter=8))
    
    styles.add(ParagraphStyle(name='Normal',
                             fontName='Helvetica',
                             fontSize=12,
                             spaceAfter=6))
    
    styles.add(ParagraphStyle(name='Bullet',
                             fontName='Helvetica',
                             fontSize=12,
                             leftIndent=20,
                             spaceAfter=3))
    
    # Build content
    elements = []
    
    # Cover page
    elements.append(Paragraph(f"{title}", styles['Title']))
    elements.append(Spacer(1, 0.25*inch))
    elements.append(Paragraph(f"{adaptation_type} Pitch Deck", styles['Subtitle']))
    elements.append(Spacer(1, 0.5*inch))
    
    # Add poster image if available
    if poster_image_url:
        img_data = download_image(poster_image_url)
        if img_data:
            img = Image(img_data, width=5*inch, height=7*inch)
            elements.append(img)
    
    # Date
    current_date = datetime.now().strftime("%B %d, %Y")
    elements.append(Spacer(1, 0.5*inch))
    elements.append(Paragraph(f"Prepared: {current_date}", styles['Normal']))
    elements.append(Paragraph("Generated with IP Pitch Builder", styles['Normal']))
    
    # Page break
    elements.append(Spacer(1, 1*inch))
    
    # Pitch content
    if pitch_content:
        elements.append(Paragraph("EXECUTIVE SUMMARY", styles['Heading1']))
        elements.append(Spacer(1, 0.1*inch))
        
        elements.append(Paragraph("High Concept:", styles['Heading2']))
        elements.append(Paragraph(pitch_content.get('high_concept', ''), styles['Normal']))
        elements.append(Spacer(1, 0.1*inch))
        
        elements.append(Paragraph("Logline:", styles['Heading2']))
        elements.append(Paragraph(pitch_content.get('logline', ''), styles['Normal']))
        elements.append(Spacer(1, 0.2*inch))
        
        # Unique selling points
        elements.append(Paragraph("Unique Selling Points:", styles['Heading2']))
        for point in pitch_content.get('unique_selling_points', []):
            elements.append(Paragraph(f"• {point}", styles['Bullet']))
        elements.append(Spacer(1, 0.2*inch))
        
        # Visual style and franchise potential
        elements.append(Paragraph("Visual Style:", styles['Heading2']))
        elements.append(Paragraph(pitch_content.get('visual_style', ''), styles['Normal']))
        elements.append(Spacer(1, 0.1*inch))
        
        if 'franchise_potential' in pitch_content:
            elements.append(Paragraph("Franchise Potential:", styles['Heading2']))
            elements.append(Paragraph(pitch_content['franchise_potential'], styles['Normal']))
            elements.append(Spacer(1, 0.1*inch))
        
        # Comparable titles
        elements.append(Paragraph("Comparable Titles:", styles['Heading2']))
        comp_titles = pitch_content.get('comp_titles', [])
        if comp_titles:
            comp_text = ", ".join(comp_titles)
            elements.append(Paragraph(comp_text, styles['Normal']))
        
        # Page break
        elements.append(Spacer(1, 1*inch))
    
    # Plot synopsis
    if plot_synopsis:
        elements.append(Paragraph("STORY", styles['Heading1']))
        elements.append(Spacer(1, 0.1*inch))
        
        elements.append(Paragraph("Synopsis:", styles['Heading2']))
        elements.append(Paragraph(plot_synopsis.get('short_synopsis', ''), styles['Normal']))
        elements.append(Spacer(1, 0.2*inch))
        
        elements.append(Paragraph("Detailed Synopsis:", styles['Heading2']))
        elements.append(Paragraph(plot_synopsis.get('detailed_synopsis', ''), styles['Normal']))
        elements.append(Spacer(1, 0.2*inch))
        
        # Act structure
        elements.append(Paragraph("Structure:", styles['Heading2']))
        for act in plot_synopsis.get('act_structure', []):
            elements.append(Paragraph(f"• {act}", styles['Bullet']))
        
        # Page break
        elements.append(Spacer(1, 1*inch))
    
    # Character profiles
    if character_profiles:
        elements.append(Paragraph("CHARACTERS", styles['Heading1']))
        elements.append(Spacer(1, 0.1*inch))
        
        for i, character in enumerate(character_profiles):
            elements.append(Paragraph(f"{character.get('name', '')} - {character.get('role', '')}", styles['Heading2']))
            elements.append(Paragraph(f"<b>Description:</b> {character.get('description', '')}", styles['Normal']))
            elements.append(Paragraph(f"<b>Arc:</b> {character.get('arc', '')}", styles['Normal']))
            
            traits = character.get('key_traits', [])
            if traits:
                elements.append(Paragraph(f"<b>Key Traits:</b> {', '.join(traits)}", styles['Normal']))
            
            # Only add spacer if not the last character
            if i < len(character_profiles) - 1:
                elements.append(Spacer(1, 0.2*inch))
        
        # Page break
        elements.append(Spacer(1, 1*inch))
    
    # Cast suggestions
    if cast_suggestions:
        elements.append(Paragraph("PROPOSED CAST", styles['Heading1']))
        elements.append(Spacer(1, 0.1*inch))
        elements.append(Paragraph(cast_suggestions, styles['Normal']))
        elements.append(Spacer(1, 1*inch))
    
    # Teaser trailer script
    if teaser_script:
        elements.append(Paragraph("TEASER TRAILER", styles['Heading1']))
        elements.append(Spacer(1, 0.1*inch))
        
        elements.append(Paragraph(f"<b>Duration:</b> {teaser_script.get('duration', '')}", styles['Normal']))
        elements.append(Spacer(1, 0.1*inch))
        
        elements.append(Paragraph("<b>Voiceover:</b>", styles['Heading2']))
        elements.append(Paragraph(f'"{teaser_script.get("voiceover", "")}"', styles['Normal']))
        elements.append(Spacer(1, 0.1*inch))
        
        elements.append(Paragraph("<b>Scenes:</b>", styles['Heading2']))
        for i, scene in enumerate(teaser_script.get('scenes', []), 1):
            elements.append(Paragraph(f"Scene {i}: {scene}", styles['Bullet']))
        elements.append(Spacer(1, 0.1*inch))
        
        elements.append(Paragraph(f"<b>Music:</b> {teaser_script.get('music_suggestion', '')}", styles['Normal']))
        elements.append(Paragraph(f"<b>Sound Effects:</b> {teaser_script.get('sound_effects', '')}", styles['Normal']))
        elements.append(Paragraph(f"<b>Title Treatment:</b> {teaser_script.get('title_treatment', '')}", styles['Normal']))
        
        # Page break
        elements.append(Spacer(1, 1*inch))
    
    # Market analysis
    if market_analysis:
        elements.append(Paragraph("MARKET ANALYSIS", styles['Heading1']))
        elements.append(Spacer(1, 0.1*inch))
        elements.append(Paragraph(market_analysis, styles['Normal']))
    
    # Build and save PDF
    doc.build(elements)
    
    return output_path 