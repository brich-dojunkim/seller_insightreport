# pdf/styles.py - PDF 스타일 및 레이아웃 정의

from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.lib import colors
from reportlab.lib.units import inch, cm
import sys
sys.path.append('..')
from config import COLORS, FONTS, FONT_SIZES, PDF_SETTINGS

class PDFStyles:
    """PDF 문서 스타일 관리 클래스"""
    
    def __init__(self):
        self.colors = COLORS
        self.fonts = FONTS
        self.font_sizes = FONT_SIZES
        self.base_styles = getSampleStyleSheet()
        self.custom_styles = self._create_custom_styles()
    
    def _create_custom_styles(self):
        """커스텀 스타일 생성"""
        styles = {}
        
        # === 제목 스타일 ===
        styles['title'] = ParagraphStyle(
            'BFlowTitle',
            parent=self.base_styles['Heading1'],
            fontSize=self.font_sizes['title'],
            fontName=self.fonts['title'],
            textColor=colors.HexColor(self.colors['primary']),
            alignment=TA_LEFT,
            spaceAfter=20,
            spaceBefore=10
        )
        
        styles['subtitle'] = ParagraphStyle(
            'BFlowSubtitle',
            parent=self.base_styles['Heading2'],
            fontSize=self.font_sizes['subtitle'],
            fontName=self.fonts['heading'],
            textColor=colors.HexColor(self.colors['secondary']),
            alignment=TA_LEFT,
            spaceAfter=15,
            spaceBefore=15
        )
        
        # === 헤딩 스타일 ===
        styles['heading'] = ParagraphStyle(
            'BFlowHeading',
            parent=self.base_styles['Heading2'],
            fontSize=self.font_sizes['heading'],
            fontName=self.fonts['heading'],
            textColor=colors.HexColor(self.colors['primary']),
            alignment=TA_LEFT,
            spaceAfter=12,
            spaceBefore=20
        )
        
        styles['subheading'] = ParagraphStyle(
            'BFlowSubheading',
            parent=self.base_styles['Heading3'],
            fontSize=self.font_sizes['subheading'],
            fontName=self.fonts['heading'],
            textColor=colors.HexColor(self.colors['dark_gray']),
            alignment=TA_LEFT,
            spaceAfter=10,
            spaceBefore=15
        )
        
        # === 본문 스타일 ===
        styles['body'] = ParagraphStyle(
            'BFlowBody',
            parent=self.base_styles['Normal'],
            fontSize=self.font_sizes['body'],
            fontName=self.fonts['body'],
            textColor=colors.HexColor(self.colors['dark_gray']),
            alignment=TA_LEFT,
            spaceAfter=6,
            leading=14
        )
        
        styles['body_center'] = ParagraphStyle(
            'BFlowBodyCenter',
            parent=styles['body'],
            alignment=TA_CENTER
        )
        
        styles['body_right'] = ParagraphStyle(
            'BFlowBodyRight',
            parent=styles['body'],
            alignment=TA_RIGHT
        )
        
        # === 특수 스타일 ===
        styles['caption'] = ParagraphStyle(
            'BFlowCaption',
            parent=self.base_styles['Normal'],
            fontSize=self.font_sizes['caption'],
            fontName=self.fonts['caption'],
            textColor=colors.HexColor(self.colors['medium_gray']),
            alignment=TA_CENTER,
            spaceAfter=4,
            leading=11
        )
        
        styles['highlight'] = ParagraphStyle(
            'BFlowHighlight',
            parent=styles['body'],
            textColor=colors.HexColor(self.colors['primary']),
            fontName=self.fonts['heading'],
            backColor=colors.HexColor(self.colors['light_gray']),
            borderColor=colors.HexColor(self.colors['primary']),
            borderWidth=1,
            borderPadding=8
        )
        
        styles['insight_box'] = ParagraphStyle(
            'BFlowInsightBox',
            parent=styles['body'],
            textColor=colors.HexColor(self.colors['dark_gray']),
            backColor=colors.HexColor('#F8F9FA'),
            borderColor=colors.HexColor(self.colors['border']),
            borderWidth=1,
            borderPadding=12,
            spaceAfter=10
        )
        
        # === 커버 페이지 스타일 ===
        styles['cover_title'] = ParagraphStyle(
            'CoverTitle',
            fontSize=28,
            fontName=self.fonts['title'],
            textColor=colors.HexColor(self.colors['primary']),
            alignment=TA_LEFT,
            spaceAfter=10
        )
        
        styles['cover_subtitle'] = ParagraphStyle(
            'CoverSubtitle',
            fontSize=16,
            fontName=self.fonts['body'],
            textColor=colors.HexColor(self.colors['medium_gray']),
            alignment=TA_LEFT,
            spaceAfter=30
        )
        
        styles['cover_company'] = ParagraphStyle(
            'CoverCompany',
            fontSize=24,
            fontName=self.fonts['title'],
            textColor=colors.HexColor(self.colors['secondary']),
            alignment=TA_LEFT,
            spaceAfter=20
        )
        
        # === 리스트 스타일 ===
        styles['bullet_list'] = ParagraphStyle(
            'BulletList',
            parent=styles['body'],
            leftIndent=20,
            bulletIndent=10,
            spaceAfter=4
        )
        
        styles['numbered_list'] = ParagraphStyle(
            'NumberedList',
            parent=styles['body'],
            leftIndent=20,
            bulletIndent=10,
            spaceAfter=4
        )
        
        return styles
    
    def get_table_styles(self):
        """테이블 스타일 정의"""
        from reportlab.platypus import TableStyle
        
        styles = {}
        
        # 기본 테이블 스타일
        styles['default'] = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(self.colors['primary'])),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), self.fonts['heading']),
            ('FONTSIZE', (0, 0), (-1, 0), self.font_sizes['body']),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor(self.colors['light_gray'])),
            ('FONTNAME', (0, 1), (-1, -1), self.fonts['body']),
            ('FONTSIZE', (0, 1), (-1, -1), self.font_sizes['caption']),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor(self.colors['border'])),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
        ])
        
        # KPI 테이블 스타일
        styles['kpi'] = TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, -1), self.fonts['heading']),
            ('FONTSIZE', (0, 0), (-1, -1), self.font_sizes['body']),
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor(self.colors['light_gray'])),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor(self.colors['border'])),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10)
        ])
        
        # 채널 성과 테이블 스타일
        styles['channel'] = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(self.colors['secondary'])),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), self.fonts['heading']),
            ('FONTSIZE', (0, 0), (-1, -1), self.font_sizes['caption']),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), 
             [colors.white, colors.HexColor(self.colors['light_gray'])]),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor(self.colors['border']))
        ])
        
        # 깔끔한 테이블 스타일 (테두리 최소화)
        styles['clean'] = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(self.colors['light_gray'])),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor(self.colors['dark_gray'])),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), self.fonts['heading']),
            ('FONTNAME', (0, 1), (-1, -1), self.fonts['body']),
            ('FONTSIZE', (0, 0), (-1, -1), self.font_sizes['caption']),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('LINEBELOW', (0, 0), (-1, 0), 2, colors.HexColor(self.colors['primary'])),
            ('LINEBELOW', (0, -1), (-1, -1), 1, colors.HexColor(self.colors['border']))
        ])
        
        return styles
    
    def get_color_scheme(self):
        """색상 스키마 반환"""
        return {
            'primary': colors.HexColor(self.colors['primary']),
            'secondary': colors.HexColor(self.colors['secondary']),
            'accent': colors.HexColor(self.colors['accent']),
            'success': colors.HexColor(self.colors['success']),
            'warning': colors.HexColor(self.colors['warning']),
            'danger': colors.HexColor(self.colors['danger']),
            'light_gray': colors.HexColor(self.colors['light_gray']),
            'medium_gray': colors.HexColor(self.colors['medium_gray']),
            'dark_gray': colors.HexColor(self.colors['dark_gray']),
            'border': colors.HexColor(self.colors['border']),
            'white': colors.white,
            'black': colors.black
        }
    
    def get_layout_settings(self):
        """레이아웃 설정 반환"""
        return {
            'margins': {
                'top': PDF_SETTINGS['margins']['top'] * cm,
                'bottom': PDF_SETTINGS['margins']['bottom'] * cm,
                'left': PDF_SETTINGS['margins']['left'] * cm,
                'right': PDF_SETTINGS['margins']['right'] * cm
            },
            'spacing': {
                'section': PDF_SETTINGS['section_spacing'] * cm,
                'paragraph': 0.2 * cm,
                'line': 0.1 * cm
            },
            'image': {
                'small': (6 * cm, 4 * cm),
                'medium': (10 * cm, 7 * cm),
                'large': (15 * cm, 10 * cm),
                'chart': (14 * cm, 8 * cm)
            }
        }
    
    def create_section_divider(self, width=15*cm, height=0.1*cm, color=None):
        """섹션 구분선 생성"""
        if color is None:
            color = colors.HexColor(self.colors['primary'])
        
        from reportlab.graphics.shapes import Drawing, Rect
        from reportlab.graphics import renderPDF
        
        d = Drawing(width, height)
        d.add(Rect(0, 0, width, height, fillColor=color, strokeColor=None))
        return d
    
    def create_highlight_box(self, width=15*cm, height=3*cm, 
                           bg_color=None, border_color=None):
        """하이라이트 박스 생성"""
        if bg_color is None:
            bg_color = colors.HexColor(self.colors['light_gray'])
        if border_color is None:
            border_color = colors.HexColor(self.colors['primary'])
        
        from reportlab.graphics.shapes import Drawing, Rect
        
        d = Drawing(width, height)
        d.add(Rect(0, 0, width, height, 
                  fillColor=bg_color, strokeColor=border_color, strokeWidth=1))
        return d

# 전역 스타일 인스턴스
pdf_styles = PDFStyles()

# 편의 함수들
def get_style(name):
    """스타일 가져오기"""
    return pdf_styles.custom_styles.get(name, pdf_styles.base_styles['Normal'])

def get_table_style(name):
    """테이블 스타일 가져오기"""
    return pdf_styles.get_table_styles().get(name, pdf_styles.get_table_styles()['default'])

def get_color(name):
    """색상 가져오기"""
    return pdf_styles.get_color_scheme().get(name, colors.black)

def get_layout():
    """레이아웃 설정 가져오기"""
    return pdf_styles.get_layout_settings()