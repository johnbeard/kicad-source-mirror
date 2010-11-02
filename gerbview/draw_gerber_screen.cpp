/****************/
/* tracepcb.cpp */
/****************/

/*
 *  Redraw the screen.
 */

#include "fctsys.h"
#include "gr_basic.h"
#include "common.h"
#include "class_drawpanel.h"
#include "drawtxt.h"

#include "gerbview.h"
#include "class_board_design_settings.h"
#include "colors_selection.h"
#include "class_gerber_draw_item.h"
#include "class_GERBER.h"

static void Show_Items_DCode_Value( WinEDA_DrawPanel* panel, wxDC* DC,
                                    BOARD* Pcb, int drawmode );

/** virtual Function PrintPage
 * Used to print the board (on printer, or when creating SVF files).
 * Print the board, but only layers allowed by aPrintMaskLayer
 * @param aDC = the print device context
 * @param aPrint_Sheet_Ref = true to print frame references
 * @param aPrintMasklayer = a 32 bits mask: bit n = 1 -> layer n is printed
 * @param aPrintMirrorMode = true to plot mirrored
 * @param aData = a pointer to an optional data (not used here: can be NULL)
 */
void WinEDA_GerberFrame::PrintPage( wxDC* aDC, bool aPrint_Sheet_Ref, int aPrintMasklayer,
                                    bool aPrintMirrorMode, void* aData )
{
    // Save current draw options, because print mode has specfic options:
    int             DisplayPolygonsModeImg = g_DisplayPolygonsModeSketch;
    int             visiblemask = GetBoard()->GetVisibleLayers();
    DISPLAY_OPTIONS save_opt    = DisplayOpt;

    // Set draw options for printing:
    GetBoard()->SetVisibleLayers( aPrintMasklayer );
    DisplayOpt.DisplayPcbTrackFill = FILLED;
    DisplayOpt.DisplayDrawItems    = FILLED;
    DisplayOpt.DisplayZonesMode    = 0;
    g_DisplayPolygonsModeSketch    = 0;

    DrawPanel->m_PrintIsMirrored = aPrintMirrorMode;

    GetBoard()->Draw( DrawPanel, aDC, GR_COPY, wxPoint( 0, 0 ) );

    if( aPrint_Sheet_Ref )
        TraceWorkSheet( aDC, GetScreen(), 0 );

    DrawPanel->m_PrintIsMirrored = false;

    // Restore draw options:
    GetBoard()->SetVisibleLayers( visiblemask );
    DisplayOpt = save_opt;
    g_DisplayPolygonsModeSketch = DisplayPolygonsModeImg;
}


/*******************************************************************/
void WinEDA_GerberFrame::RedrawActiveWindow( wxDC* DC, bool EraseBg )
/*******************************************************************/

/* Redraws the full screen, including axis and grid
 */
{
    PCB_SCREEN* screen = (PCB_SCREEN*) GetScreen();

    if( !GetBoard() )
        return;
    ActiveScreen = screen;

    GRSetDrawMode( DC, GR_COPY );
    DrawPanel->DrawBackGround( DC );

    GetBoard()->Draw( DrawPanel, DC, GR_COPY, wxPoint( 0, 0 ) );

    if( IsElementVisible( DCODES_VISIBLE ) )
        Show_Items_DCode_Value( DrawPanel, DC, GetBoard(), GR_COPY );

    TraceWorkSheet( DC, screen, 0 );

    if( DrawPanel->ManageCurseur )
        DrawPanel->ManageCurseur( DrawPanel, DC, FALSE );

    DrawPanel->DrawCursor( DC );

    // Display the filename and the layer name (found in the gerber files, if any)
    // relative to the active layer
    UpdateTitleAndInfo();
}


/********************************************************************/
void BOARD::Draw( WinEDA_DrawPanel* aPanel, wxDC* aDC, int aDrawMode, const wxPoint& aOffset )
/********************************************************************/
/* Redraw the BOARD items but not cursors, axis or grid */
{
    // Because Images can be negative (i.e with background filled in color) items are drawn
    // graphic layer per graphic layer, after the background is filled
    for( int layer = 0; layer < 32; layer++ )
    {
        if( !GetBoard()->IsLayerVisible( layer ) )
            continue;
        GERBER_IMAGE* gerber = g_GERBER_List[layer];
        if( gerber == NULL )    // Graphic layer not yet used
            continue;

        /* Draw background negative (i.e. in graphic layer color) for negative images:
         *  Background is drawn here in GR_OR mode because in COPY mode
         *  all previous graphics will be erased
         *  Note: items in background color ("Erased" items) are always drawn in COPY mode
         *  Some artifacts can happen when more than one gerber file is loaded
         */
        if( gerber->m_ImageNegative )
        {
            int       color = GetBoard()->GetLayerColor( layer );
            GRSetDrawMode( aDC, GR_OR );
            EDA_Rect* cbox = &aPanel->m_ClipBox;
            GRSFilledRect( cbox, aDC, cbox->GetX(), cbox->GetY(),
                           cbox->GetRight(), cbox->GetBottom(),
                           0, color, color );
            GRSetDrawMode( aDC, aDrawMode );
        }

        int         dcode_hightlight = 0;
        if( layer == m_PcbFrame->GetScreen()->m_Active_Layer )
            dcode_hightlight = gerber->m_Selected_Tool;
        BOARD_ITEM* item = GetBoard()->m_Drawings;
        for( ; item; item = item->Next() )
        {
            GERBER_DRAW_ITEM* gerb_item = (GERBER_DRAW_ITEM*) item;
            if( gerb_item->GetLayer()!= layer )
                continue;
            int drawMode = aDrawMode;
            if( dcode_hightlight == gerb_item->m_DCode )
                drawMode |= GR_SURBRILL;
            gerb_item->Draw( aPanel, aDC, drawMode );
        }
    }

    m_PcbFrame->GetScreen()->ClrRefreshReq();
}


/*****************************************************************************************/
void Show_Items_DCode_Value( WinEDA_DrawPanel* aPanel, wxDC* aDC, BOARD* aPcb, int aDrawMode )
/*****************************************************************************************/
{
    wxPoint     pos;
    int         width, orient;
    wxString    Line;

    GRSetDrawMode( aDC, aDrawMode );
    BOARD_ITEM* item = aPcb->m_Drawings;
    for( ; item != NULL; item = item->Next() )
    {
        GERBER_DRAW_ITEM* gerb_item = (GERBER_DRAW_ITEM*) item;
        if( aPcb->IsLayerVisible( gerb_item->GetLayer() ) == false )
            continue;
        if( gerb_item->m_DCode <= 0 )
            continue;

        if( gerb_item->m_Flashed || gerb_item->m_Shape == GBR_ARC )
            pos = gerb_item->m_Start;
        else
        {
            pos.x = (gerb_item->m_Start.x + gerb_item->m_End.x) / 2;
            pos.y = (gerb_item->m_Start.y + gerb_item->m_End.y) / 2;
        }

        pos = gerb_item->GetABPosition( pos );

        Line.Printf( wxT( "D%d" ), gerb_item->m_DCode );

        if( gerb_item->GetDcodeDescr() )
            width  = gerb_item->GetDcodeDescr()->GetShapeDim( gerb_item );
        else
            width  = MIN( gerb_item->m_Size.x, gerb_item->m_Size.y );

        orient = TEXT_ORIENT_HORIZ;
        if( gerb_item->m_Flashed )
        {
            // A reasonnable size for text is width/3 because most ot time this text has 3 chars.
            width /= 3;
        }
        else        // this item is a line
        {
            wxPoint delta = gerb_item->m_Start - gerb_item->m_End;
            if( abs( delta.x ) < abs( delta.y ) )
                orient = TEXT_ORIENT_VERT;
            // A reasonnable size for text is width/2 because text needs margin below and above it.
            // a margin = width/4 seems good
            width /= 2;
        }

        int color = g_ColorsSettings.GetItemColor( DCODES_VISIBLE );

        DrawGraphicText( aPanel, aDC,
                         pos, (EDA_Colors) color, Line,
                         orient, wxSize( width, width ),
                         GR_TEXT_HJUSTIFY_CENTER, GR_TEXT_VJUSTIFY_CENTER,
                         0, false, false, false );
    }
}


/* Virtual fonction needed by the PCB_SCREEN class derived from BASE_SCREEN
 * this is a virtual pure function in BASE_SCREEN
 * do nothing in gerbview
 * could be removed later
 */
void PCB_SCREEN::ClearUndoORRedoList( UNDO_REDO_CONTAINER&, int )
{
}