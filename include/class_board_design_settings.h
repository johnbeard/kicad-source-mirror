/**********************************************************/
/*  class_board_design_settings.h :  handle board options */
/**********************************************************/

#ifndef BOARD_DESIGN_SETTINGS_H_
#define BOARD_DESIGN_SETTINGS_H_

#include <pcbstruct.h>      // NB_COLORS
#include <class_pad.h>
#include <class_track.h>
#include <class_netclass.h>
#include <config_params.h>

/**
 * Struct VIA_DIMENSION
 * is a small helper container to handle a stock of specific vias each with
 * unique diameter and drill sizes in the BOARD class.
 */
struct VIA_DIMENSION
{
    int m_Diameter;     // <= 0 means use Netclass via diameter
    int m_Drill;        // <= 0 means use Netclass via drill

    VIA_DIMENSION()
    {
        m_Diameter = 0;
        m_Drill    = 0;
    }

    VIA_DIMENSION( int aDiameter, int aDrill )
    {
        m_Diameter = aDiameter;
        m_Drill    = aDrill;
    }

    bool operator==( const VIA_DIMENSION& aOther ) const
    {
        return ( m_Diameter == aOther.m_Diameter ) && ( m_Drill == aOther.m_Drill );
    }

    bool operator<( const VIA_DIMENSION& aOther ) const
    {
        if( m_Diameter != aOther.m_Diameter )
            return m_Diameter < aOther.m_Diameter;

        return m_Drill < aOther.m_Drill;
    }
};

/**
 * Class BOARD_DESIGN_SETTINGS
 * contains design settings for a BOARD object.
 */
class BOARD_DESIGN_SETTINGS
{
public:
    // The first value is the current netclass via size
    /// Vias size and drill list
    std::vector<VIA_DIMENSION> m_ViasDimensionsList;

    // The first value is the current netclass track width
    /// Track width list
    std::vector<int> m_TrackWidthList;

    /// List of current netclasses. There is always the default netclass.
    NETCLASSES m_NetClasses;

    bool    m_MicroViasAllowed;             ///< true to allow micro vias
    bool    m_BlindBuriedViaAllowed;        ///< true to allow blind/buried vias
    VIATYPE_T m_CurrentViaType;             ///< via type (VIA_BLIND_BURIED, VIA_THROUGH VIA_MICROVIA)

    /// if true, when creating a new track starting on an existing track, use this track width
    bool    m_UseConnectedTrackWidth;
    int     m_DrawSegmentWidth;             ///< current graphic line width (not EDGE layer)
    int     m_EdgeSegmentWidth;             ///< current graphic line width (EDGE layer only)
    int     m_PcbTextWidth;                 ///< current Pcb (not module) Text width
    wxSize  m_PcbTextSize;                  ///< current Pcb (not module) Text size
    int     m_TrackMinWidth;                ///< track min value for width ((min copper size value
    int     m_ViasMinSize;                  ///< vias (not micro vias) min diameter
    int     m_ViasMinDrill;                 ///< vias (not micro vias) min drill diameter
    int     m_MicroViasMinSize;             ///< micro vias (not vias) min diameter
    int     m_MicroViasMinDrill;            ///< micro vias (not vias) min drill diameter

    // Global mask margins:
    int     m_SolderMaskMargin;             ///< Solder mask margin
    int     m_SolderMaskMinWidth;           ///< Solder mask min width
                                            // 2 areas near than m_SolderMaskMinWidth
                                            // are merged
    int     m_SolderPasteMargin;            ///< Solder paste margin absolute value
    double  m_SolderPasteMarginRatio;       ///< Solder pask margin ratio value of pad size
                                            ///< The final margin is the sum of these 2 values

    // Variables used in footprint handling
    wxSize  m_ModuleTextSize;               ///< Default footprint texts size
    int     m_ModuleTextWidth;
    int     m_ModuleSegmentWidth;
    wxPoint m_AuxOrigin;                    ///< origin for plot exports
    wxPoint m_GridOrigin;                   ///< origin for grid offsets

    D_PAD   m_Pad_Master;

    BOARD_DESIGN_SETTINGS();

    /**
     * Function GetDefault
     * @return the default netclass.
     */
    inline NETCLASSPTR GetDefault() const
    {
        return m_NetClasses.GetDefault();
    }

    /**
     * Function GetCurrentNetClassName
     * @return the current net class name.
     */
    inline const wxString& GetCurrentNetClassName() const
    {
        return m_currentNetClassName;
    }

    /**
     * Function UseNetClassTrack
     * returns true if netclass values should be used to obtain appropriate track width.
     */
    inline bool UseNetClassTrack() const
    {
        return ( m_trackWidthIndex == 0 && !m_useCustomTrackVia );
    }

    /**
     * Function UseNetClassVia
     * returns true if netclass values should be used to obtain appropriate via size.
     */
    inline bool UseNetClassVia() const
    {
        return ( m_viaSizeIndex == 0 && !m_useCustomTrackVia );
    }

    /**
     * Function SetCurrentNetClass
     * Must be called after a netclass selection (or after a netclass parameter change
     * Initialize vias and tracks values displayed in comb boxes of the auxiliary toolbar
     * and some others parameters (netclass name ....)
     * @param aNetClassName = the new netclass name
     * @return true if lists of tracks and vias sizes are modified
     */
    bool SetCurrentNetClass( const wxString& aNetClassName );

    /**
     * Function GetBiggestClearanceValue
     * @return the biggest clearance value found in NetClasses list
     */
    int GetBiggestClearanceValue();

    /**
     * Function GetSmallestClearanceValue
     * @return the smallest clearance value found in NetClasses list
     */
    int GetSmallestClearanceValue();

    /**
     * Function GetCurrentMicroViaSize
     * @return the current micro via size,
     * that is the current netclass value
     */
    int GetCurrentMicroViaSize();

    /**
     * Function GetCurrentMicroViaDrill
     * @return the current micro via drill,
     * that is the current netclass value
     */
    int GetCurrentMicroViaDrill();

    /**
     * Function GetTrackWidthIndex
     * @return the current track width list index.
     */
    inline unsigned GetTrackWidthIndex() const { return m_trackWidthIndex; }

    /**
     * Function SetTrackWidthIndex
     * sets the current track width list index to \a aIndex.
     *
     * @param aIndex is the track width list index.
     */
    void SetTrackWidthIndex( unsigned aIndex );

    /**
     * Function GetCurrentTrackWidth
     * @return the current track width, according to the selected options
     * ( using the default netclass value or a preset/custom value )
     * the default netclass is always in m_TrackWidthList[0]
     */
    inline int GetCurrentTrackWidth() const
    {
        return m_useCustomTrackVia ? m_customTrackWidth : m_TrackWidthList[m_trackWidthIndex];
    }

    /**
     * Function SetCustomTrackWidth
     * Sets custom width for track (i.e. not available in netclasses or preset list). To have
     * it returned with GetCurrentTrackWidth() you need to enable custom track & via sizes
     * (UseCustomTrackViaSize()).
     * @param aWidth is the new track width.
     */
    inline void SetCustomTrackWidth( int aWidth )
    {
        m_customTrackWidth = aWidth;
    }

    /**
     * Function GetCustomTrackWidth
     * @return Current custom width for a track.
     */
    inline int GetCustomTrackWidth() const
    {
        return m_customTrackWidth;
    }

    /**
     * Function GetViaSizeIndex
     * @return the current via size list index.
     */
    inline unsigned GetViaSizeIndex() const
    {
        return m_viaSizeIndex;
    }

    /**
     * Function SetViaSizeIndex
     * sets the current via size list index to \a aIndex.
     *
     * @param aIndex is the via size list index.
     */
    void SetViaSizeIndex( unsigned aIndex );

    /**
     * Function GetCurrentViaSize
     * @return the current via size, according to the selected options
     * ( using the default netclass value or a preset/custom value )
     * the default netclass is always in m_TrackWidthList[0]
     */
    inline int GetCurrentViaSize() const
    {
        if( m_useCustomTrackVia )
            return m_customViaSize.m_Diameter;
        else
            return m_ViasDimensionsList[m_viaSizeIndex].m_Diameter;
    }

    /**
     * Function SetCustomViaSize
     * Sets custom size for via diameter (i.e. not available in netclasses or preset list). To have
     * it returned with GetCurrentViaSize() you need to enable custom track & via sizes
     * (UseCustomTrackViaSize()).
     * @param aSize is the new drill diameter.
     */
    inline void SetCustomViaSize( int aSize )
    {
        m_customViaSize.m_Diameter = aSize;
    }

    /**
     * Function GetCustomViaSize
     * @return Current custom size for the via diameter.
     */
    inline int GetCustomViaSize() const
    {
        return m_customViaSize.m_Diameter;
    }

    /**
     * Function GetCurrentViaDrill
     * @return the current via size, according to the selected options
     * ( using the default netclass value or a preset/custom value )
     * the default netclass is always in m_TrackWidthList[0]
     */
    int GetCurrentViaDrill() const;

    /**
     * Function SetCustomViaDrill
     * Sets custom size for via drill (i.e. not available in netclasses or preset list). To have
     * it returned with GetCurrentViaDrill() you need to enable custom track & via sizes
     * (UseCustomTrackViaSize()).
     * @param aDrill is the new drill size.
     */
    inline void SetCustomViaDrill( int aDrill )
    {
        m_customViaSize.m_Drill = aDrill;
    }

    /**
     * Function GetCustomViaDrill
     * @return Current custom size for the via drill.
     */
    inline int GetCustomViaDrill() const
    {
        return m_customViaSize.m_Drill;
    }

    /**
     * Function UseCustomTrackViaSize
     * Enables/disables custom track/via size settings. If enabled, values set with
     * SetCustomTrackWidth()/SetCustomViaSize()/SetCustomViaDrill() are used for newly created
     * tracks and vias.
     * @param aEnabled decides if custom settings should be used for new tracks/vias.
     */
    inline void UseCustomTrackViaSize( bool aEnabled )
    {
        m_useCustomTrackVia = aEnabled;
    }

    /**
     * Function UseCustomTrackViaSize
     * @return True if custom sizes of tracks & vias are enabled, false otherwise.
     */
    inline bool UseCustomTrackViaSize() const
    {
        return m_useCustomTrackVia;
    }

    /**
     * Function GetVisibleLayers
     * returns a bit-mask of all the layers that are visible
     * @return int - the visible layers in bit-mapped form.
     */
    inline LAYER_MSK GetVisibleLayers() const
    {
        return m_visibleLayers;
    }

    /**
     * Function SetVisibleAlls
     * Set the bit-mask of all visible elements categories,
     * including enabled layers
     */
    void SetVisibleAlls();

    /**
     * Function SetVisibleLayers
     * changes the bit-mask of visible layers
     * @param aMask = The new bit-mask of visible layers
     */
    inline void SetVisibleLayers( LAYER_MSK aMask )
    {
        m_visibleLayers = aMask & m_enabledLayers & FULL_LAYERS;
    }

    /**
     * Function IsLayerVisible
     * tests whether a given layer is visible
     * @param aLayer = The layer to be tested
     * @return bool - true if the layer is visible.
     */
    inline bool IsLayerVisible( LAYER_NUM aLayer ) const
    {
        // If a layer is disabled, it is automatically invisible
        return m_visibleLayers & m_enabledLayers & GetLayerMask( aLayer );
    }

    /**
     * Function SetLayerVisibility
     * changes the visibility of a given layer
     * @param aLayer = The layer to be changed
     * @param aNewState = The new visibility state of the layer
     */
    void SetLayerVisibility( LAYER_NUM aLayer, bool aNewState );

    /**
     * Function GetVisibleElements
     * returns a bit-mask of all the element categories that are visible
     * @return int - the visible element categories in bit-mapped form.
     */
    inline int GetVisibleElements() const
    {
        return m_visibleElements;
    }

    /**
     * Function SetVisibleElements
     * changes the bit-mask of visible element categories
     * @param aMask = The new bit-mask of visible element categories
     */
    inline void SetVisibleElements( int aMask )
    {
        m_visibleElements = aMask;
    }

    /**
     * Function IsElementVisible
     * tests whether a given element category is visible. Keep this as an
     * inline function.
     * @param aElementCategory is from the enum by the same name
     * @return bool - true if the element is visible.
     * @see enum PCB_VISIBLE
     */
    inline bool IsElementVisible( int aElementCategory ) const
    {
        assert( aElementCategory >= 0 && aElementCategory < END_PCB_VISIBLE_LIST );

        return ( m_visibleElements & ( 1 << aElementCategory ) );
    }

    /**
     * Function SetElementVisibility
     * changes the visibility of an element category
     * @param aElementCategory is from the enum by the same name
     * @param aNewState = The new visibility state of the element category
     * @see enum PCB_VISIBLE
     */
    void SetElementVisibility( int aElementCategory, bool aNewState );

    /**
     * Function GetEnabledLayers
     * returns a bit-mask of all the layers that are enabled
     * @return int - the enabled layers in bit-mapped form.
     */
    inline LAYER_MSK GetEnabledLayers() const
    {
        return m_enabledLayers;
    }

    /**
     * Function SetEnabledLayers
     * changes the bit-mask of enabled layers
     * @param aMask = The new bit-mask of enabled layers
     */
    void SetEnabledLayers( LAYER_MSK aMask );

    /**
     * Function IsLayerEnabled
     * tests whether a given layer is enabled
     * @param aLayer = The of the layer to be tested
     * @return bool - true if the layer is enabled
     */
    inline bool IsLayerEnabled( LAYER_NUM aLayer ) const
    {
        return m_enabledLayers & GetLayerMask( aLayer );
    }

    /**
     * Function GetCopperLayerCount
     * @return int - the number of neabled copper layers
     */
    inline int GetCopperLayerCount() const
    {
        return m_copperLayerCount;
    }

    /**
     * Function SetCopperLayerCount
     * do what its name says...
     * @param aNewLayerCount = The new number of enabled copper layers
     */
    void SetCopperLayerCount( int aNewLayerCount );

    /**
     * Function AppendConfigs
     * appends to @a aResult the configuration setting accessors which will later
     * allow reading or writing of configuration file information directly into
     * this object.
     */
    void AppendConfigs( PARAM_CFG_ARRAY* aResult );

    inline int GetBoardThickness() const { return m_boardThickness; }
    inline void SetBoardThickness( int aThickness ) { m_boardThickness = aThickness; }

private:
    /// Index for #m_ViasDimensionsList to select the current via size.
    /// 0 is the index selection of the default value Netclass
    unsigned m_viaSizeIndex;

    // Index for m_TrackWidthList to select the value.
    /// 0 is the index selection of the default value Netclass
    unsigned m_trackWidthIndex;

    ///> Use custom values for track/via sizes (not specified in net class nor in the size lists).
    bool m_useCustomTrackVia;

    ///> Custom track width (used after UseCustomTrackViaSize( true ) was called).
    int m_customTrackWidth;

    ///> Custom via size (used after UseCustomTrackViaSize( true ) was called).
    VIA_DIMENSION m_customViaSize;

    int       m_copperLayerCount;   ///< Number of copper layers for this design
    LAYER_MSK m_enabledLayers;      ///< Bit-mask for layer enabling
    LAYER_MSK m_visibleLayers;      ///< Bit-mask for layer visibility
    int       m_visibleElements;    ///< Bit-mask for element category visibility
    int       m_boardThickness;     ///< Board thickness for 3D viewer

    /// Current net class name used to display netclass info.
    /// This is also the last used netclass after starting a track.
    wxString  m_currentNetClassName;

    void formatNetClass( NETCLASS* aNetClass, OUTPUTFORMATTER* aFormatter, int aNestLevel,
                         int aControlBits ) const throw( IO_ERROR );
};

#endif  // BOARD_DESIGN_SETTINGS_H_
