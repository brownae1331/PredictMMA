import React, { useEffect, useState } from 'react';
import { 
    View, 
    Text, 
    StyleSheet, 
    ScrollView, 
    TouchableOpacity, 
    ActivityIndicator,
    Image,
    Alert 
} from 'react-native';
import { useLocalSearchParams, router } from 'expo-router';
import { getFighterById, getFighterFightHistory } from '../lib/api/fighter_api';
import { Fighter } from '../types/fighter_types';
import { FighterFightHistory } from '../types/fight_types';

export default function FighterDetailScreen() {
    const [fighter, setFighter] = useState<Fighter | null>(null);
    const [fightHistory, setFightHistory] = useState<FighterFightHistory[]>([]);
    const [loading, setLoading] = useState(true);
    const [historyLoading, setHistoryLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const { fighter_id } = useLocalSearchParams();

    useEffect(() => {
        loadFighterDetails();
    }, [fighter_id]);

    const loadFighterDetails = async () => {
        try {
            setLoading(true);
            setError(null);
            const fighterData = await getFighterById(Number(fighter_id));
            setFighter(fighterData);
            
            // Load fight history
            await loadFightHistory(Number(fighter_id));
        } catch (error) {
            console.error('Error loading fighter details:', error);
            setError(error instanceof Error ? error.message : 'Failed to load fighter details');
            Alert.alert('Error', 'Failed to load fighter details');
        } finally {
            setLoading(false);
        }
    };

    const loadFightHistory = async (fighterId: number) => {
        try {
            setHistoryLoading(true);
            const historyData = await getFighterFightHistory(fighterId);
            setFightHistory(historyData);
        } catch (error) {
            console.error('Error loading fight history:', error);
            // Don't show error for fight history, just log it
        } finally {
            setHistoryLoading(false);
        }
    };

    const formatDate = (dateString?: string) => {
        if (!dateString) return 'N/A';
        try {
            return new Date(dateString).toLocaleDateString('en-US', {
                year: 'numeric',
                month: 'long',
                day: 'numeric'
            });
        } catch {
            return dateString;
        }
    };

    const calculateAge = (dateString?: string) => {
        if (!dateString) return null;
        try {
            const birthDate = new Date(dateString);
            const today = new Date();
            let age = today.getFullYear() - birthDate.getFullYear();
            const monthDiff = today.getMonth() - birthDate.getMonth();
            if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate())) {
                age--;
            }
            return age;
        } catch {
            return null;
        }
    };

    const getResultColor = (result: string) => {
        switch (result.toLowerCase()) {
            case 'win':
                return '#4CAF50';
            case 'loss':
                return '#F44336';
            case 'draw':
                return '#FF9800';
            case 'no contest':
                return '#9E9E9E';
            default:
                return '#666';
        }
    };

    const renderFightHistoryItem = (fight: FighterFightHistory, index: number) => (
        <View key={fight.id} style={styles.fightHistoryItem}>
            <View style={styles.fightHeader}>
                <View style={styles.fightResultContainer}>
                    <Text style={[styles.fightResult, { color: getResultColor(fight.result) }]}>
                        {fight.result.toUpperCase()}
                    </Text>
                </View>
                <Text style={styles.fightDate}>{formatDate(fight.event_date || undefined)}</Text>
            </View>
            
            <Text style={styles.eventTitle} numberOfLines={1}>{fight.event_title}</Text>
            {fight.event_location && (
                <Text style={styles.eventLocation}>{fight.event_location}</Text>
            )}
            
            <View style={styles.opponentSection}>
                <View style={styles.opponentInfo}>
                    {fight.opponent_image ? (
                        <Image
                            source={{ uri: fight.opponent_image }}
                            style={styles.opponentImage}
                            defaultSource={require('../../assets/images/icon.png')}
                        />
                    ) : (
                        <View style={styles.opponentImagePlaceholder}>
                            <Text style={styles.opponentImagePlaceholderText}>
                                {fight.opponent_name.charAt(0).toUpperCase()}
                            </Text>
                        </View>
                    )}
                    <View style={styles.opponentDetails}>
                        <Text style={styles.opponentName}>{fight.opponent_name}</Text>
                        {fight.opponent_country && (
                            <Text style={styles.opponentCountry}>{fight.opponent_country}</Text>
                        )}
                        {fight.weight_class && (
                            <Text style={styles.weightClass}>{fight.weight_class}</Text>
                        )}
                    </View>
                </View>
            </View>
            
            {fight.method && (
                <View style={styles.fightDetails}>
                    <Text style={styles.fightDetailsText}>
                        {fight.method}
                        {fight.round && fight.time && ` - Round ${fight.round} (${fight.time})`}
                    </Text>
                </View>
            )}
        </View>
    );

    if (loading) {
        return (
            <View style={styles.container}>
                <View style={styles.header}>
                    <TouchableOpacity onPress={() => router.back()} style={styles.backButton}>
                        <Text style={styles.backButtonText}>← Back</Text>
                    </TouchableOpacity>
                    <Text style={styles.headerText}>Fighter Details</Text>
                    <View style={styles.placeholder} />
                </View>
                <View style={styles.loadingContainer}>
                    <ActivityIndicator size="large" color="#007AFF" />
                    <Text style={styles.loadingText}>Loading fighter details...</Text>
                </View>
            </View>
        );
    }

    if (error || !fighter) {
        return (
            <View style={styles.container}>
                <View style={styles.header}>
                    <TouchableOpacity onPress={() => router.back()} style={styles.backButton}>
                        <Text style={styles.backButtonText}>← Back</Text>
                    </TouchableOpacity>
                    <Text style={styles.headerText}>Fighter Details</Text>
                    <View style={styles.placeholder} />
                </View>
                <View style={styles.errorContainer}>
                    <Text style={styles.errorTitle}>Error</Text>
                    <Text style={styles.errorMessage}>{error || 'Fighter not found'}</Text>
                    <TouchableOpacity style={styles.retryButton} onPress={loadFighterDetails}>
                        <Text style={styles.retryButtonText}>Try Again</Text>
                    </TouchableOpacity>
                </View>
            </View>
        );
    }

    const age = calculateAge(fighter.dob);

    return (
        <View style={styles.container}>
            {/* Header with back button */}
            <View style={styles.header}>
                <TouchableOpacity onPress={() => router.back()} style={styles.backButton}>
                    <Text style={styles.backButtonText}>← Back</Text>
                </TouchableOpacity>
                <Text style={styles.headerText}>Fighter Details</Text>
                <View style={styles.placeholder} />
            </View>

            <ScrollView style={styles.scrollView} showsVerticalScrollIndicator={false}>
                <View style={styles.content}>
                    {/* Fighter Image and Basic Info */}
                    <View style={styles.fighterImageSection}>
                        {fighter.image_url ? (
                            <Image
                                source={{ uri: fighter.image_url }}
                                style={styles.fighterImage}
                                defaultSource={require('../../assets/images/icon.png')}
                            />
                        ) : (
                            <View style={styles.fighterImagePlaceholder}>
                                <Text style={styles.fighterImagePlaceholderText}>
                                    {fighter.name.charAt(0).toUpperCase()}
                                </Text>
                            </View>
                        )}
                        
                        <View style={styles.fighterBasicInfo}>
                            <Text style={styles.fighterName}>{fighter.name}</Text>
                            {fighter.nickname && (
                                <Text style={styles.fighterNickname}>"{fighter.nickname}"</Text>
                            )}
                            
                            {fighter.ranking && (
                                <View style={styles.rankingBadge}>
                                    <Text style={styles.rankingText}>#{fighter.ranking}</Text>
                                </View>
                            )}
                        </View>
                    </View>

                    {/* Fighter Stats Cards */}
                    <View style={styles.statsSection}>
                        {/* Personal Information */}
                        <View style={styles.statsCard}>
                            <Text style={styles.cardTitle}>Personal Information</Text>
                            <View style={styles.statsGrid}>
                                <View style={styles.statRow}>
                                    <Text style={styles.statLabel}>Country:</Text>
                                    <Text style={styles.statValue}>{fighter.country || 'N/A'}</Text>
                                </View>
                                {fighter.city && (
                                    <View style={styles.statRow}>
                                        <Text style={styles.statLabel}>City:</Text>
                                        <Text style={styles.statValue}>{fighter.city}</Text>
                                    </View>
                                )}
                                <View style={styles.statRow}>
                                    <Text style={styles.statLabel}>Date of Birth:</Text>
                                    <Text style={styles.statValue}>{formatDate(fighter.dob)}</Text>
                                </View>
                                {age && (
                                    <View style={styles.statRow}>
                                        <Text style={styles.statLabel}>Age:</Text>
                                        <Text style={styles.statValue}>{age} years old</Text>
                                    </View>
                                )}
                                <View style={styles.statRow}>
                                    <Text style={styles.statLabel}>Height:</Text>
                                    <Text style={styles.statValue}>{fighter.height || 'N/A'}</Text>
                                </View>
                            </View>
                        </View>

                        {/* Fighting Information */}
                        <View style={styles.statsCard}>
                            <Text style={styles.cardTitle}>Fighting Information</Text>
                            <View style={styles.statsGrid}>
                                <View style={styles.statRow}>
                                    <Text style={styles.statLabel}>Weight Class:</Text>
                                    <Text style={styles.statValue}>{fighter.weight_class || 'N/A'}</Text>
                                </View>
                                <View style={styles.statRow}>
                                    <Text style={styles.statLabel}>Record:</Text>
                                    <Text style={styles.statValue}>{fighter.record || 'N/A'}</Text>
                                </View>
                                {fighter.association && (
                                    <View style={styles.statRow}>
                                        <Text style={styles.statLabel}>Association:</Text>
                                        <Text style={styles.statValue}>{fighter.association}</Text>
                                    </View>
                                )}
                                <View style={styles.statRow}>
                                    <Text style={styles.statLabel}>Current Ranking:</Text>
                                    <Text style={styles.statValue}>
                                        {fighter.ranking ? `#${fighter.ranking}` : 'Unranked'}
                                    </Text>
                                </View>
                            </View>
                        </View>

                        {/* Quick Stats Summary */}
                        <View style={styles.quickStatsCard}>
                            <Text style={styles.cardTitle}>Quick Stats</Text>
                            <View style={styles.quickStatsRow}>
                                <View style={styles.quickStat}>
                                    <Text style={styles.quickStatNumber}>
                                        {fighter.record ? fighter.record.split('-')[0] || '0' : '0'}
                                    </Text>
                                    <Text style={styles.quickStatLabel}>Wins</Text>
                                </View>
                                <View style={styles.quickStat}>
                                    <Text style={styles.quickStatNumber}>
                                        {fighter.record ? fighter.record.split('-')[1] || '0' : '0'}
                                    </Text>
                                    <Text style={styles.quickStatLabel}>Losses</Text>
                                </View>
                                <View style={styles.quickStat}>
                                    <Text style={styles.quickStatNumber}>
                                        {fighter.record ? fighter.record.split('-')[2] || '0' : '0'}
                                    </Text>
                                    <Text style={styles.quickStatLabel}>Draws</Text>
                                </View>
                            </View>
                        </View>

                        {/* Fight History */}
                        <View style={styles.statsCard}>
                            <View style={styles.fightHistoryHeader}>
                                <Text style={styles.cardTitle}>Fight History</Text>
                                {historyLoading && (
                                    <ActivityIndicator size="small" color="#007AFF" />
                                )}
                            </View>
                            
                            {fightHistory.length > 0 ? (
                                <View style={styles.fightHistoryContainer}>
                                    {fightHistory.map((fight, index) => renderFightHistoryItem(fight, index))}
                                </View>
                            ) : (
                                <View style={styles.noHistoryContainer}>
                                    <Text style={styles.noHistoryText}>
                                        {historyLoading ? 'Loading fight history...' : 'No fight history available'}
                                    </Text>
                                </View>
                            )}
                        </View>
                    </View>
                </View>
            </ScrollView>
        </View>
    );
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: '#f5f5f5',
    },
    header: {
        backgroundColor: 'white',
        padding: 16,
        flexDirection: 'row',
        alignItems: 'center',
        justifyContent: 'space-between',
        shadowColor: '#000',
        shadowOffset: {
            width: 0,
            height: 2,
        },
        shadowOpacity: 0.1,
        shadowRadius: 3.84,
        elevation: 5,
        paddingTop: 60,
    },
    backButton: {
        padding: 8,
    },
    backButtonText: {
        fontSize: 16,
        color: '#007AFF',
        fontWeight: '600',
    },
    headerText: {
        color: 'black',
        fontWeight: 'bold',
        fontSize: 18,
    },
    placeholder: {
        width: 50,
    },
    loadingContainer: {
        flex: 1,
        justifyContent: 'center',
        alignItems: 'center',
        paddingHorizontal: 16,
    },
    loadingText: {
        marginTop: 12,
        fontSize: 16,
        color: '#666',
    },
    errorContainer: {
        flex: 1,
        justifyContent: 'center',
        alignItems: 'center',
        paddingHorizontal: 16,
    },
    errorTitle: {
        fontSize: 20,
        fontWeight: 'bold',
        color: '#FF3B30',
        marginBottom: 8,
    },
    errorMessage: {
        fontSize: 16,
        color: '#666',
        textAlign: 'center',
        lineHeight: 24,
        marginBottom: 20,
    },
    retryButton: {
        backgroundColor: '#007AFF',
        paddingHorizontal: 24,
        paddingVertical: 12,
        borderRadius: 8,
    },
    retryButtonText: {
        color: 'white',
        fontSize: 16,
        fontWeight: '600',
    },
    scrollView: {
        flex: 1,
    },
    content: {
        padding: 16,
    },
    fighterImageSection: {
        backgroundColor: 'white',
        borderRadius: 16,
        padding: 24,
        alignItems: 'center',
        marginBottom: 16,
        shadowColor: '#000',
        shadowOffset: {
            width: 0,
            height: 2,
        },
        shadowOpacity: 0.1,
        shadowRadius: 3.84,
        elevation: 5,
    },
    fighterImage: {
        width: 120,
        height: 120,
        borderRadius: 60,
        backgroundColor: '#f0f0f0',
        marginBottom: 16,
    },
    fighterImagePlaceholder: {
        width: 120,
        height: 120,
        borderRadius: 60,
        backgroundColor: '#007AFF',
        justifyContent: 'center',
        alignItems: 'center',
        marginBottom: 16,
    },
    fighterImagePlaceholderText: {
        color: 'white',
        fontSize: 36,
        fontWeight: 'bold',
    },
    fighterBasicInfo: {
        alignItems: 'center',
    },
    fighterName: {
        fontSize: 24,
        fontWeight: 'bold',
        color: '#333',
        textAlign: 'center',
        marginBottom: 8,
    },
    fighterNickname: {
        fontSize: 16,
        fontStyle: 'italic',
        color: '#666',
        textAlign: 'center',
        marginBottom: 12,
    },
    rankingBadge: {
        backgroundColor: '#007AFF',
        paddingHorizontal: 16,
        paddingVertical: 8,
        borderRadius: 20,
    },
    rankingText: {
        color: 'white',
        fontSize: 16,
        fontWeight: 'bold',
    },
    statsSection: {
        gap: 16,
    },
    statsCard: {
        backgroundColor: 'white',
        borderRadius: 12,
        padding: 20,
        shadowColor: '#000',
        shadowOffset: {
            width: 0,
            height: 2,
        },
        shadowOpacity: 0.1,
        shadowRadius: 3.84,
        elevation: 3,
    },
    cardTitle: {
        fontSize: 18,
        fontWeight: 'bold',
        color: '#333',
        marginBottom: 16,
    },
    statsGrid: {
        gap: 12,
    },
    statRow: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
        paddingVertical: 4,
    },
    statLabel: {
        fontSize: 16,
        color: '#666',
        fontWeight: '500',
        flex: 1,
    },
    statValue: {
        fontSize: 16,
        color: '#333',
        fontWeight: '600',
        textAlign: 'right',
        flex: 1,
    },
    quickStatsCard: {
        backgroundColor: '#007AFF',
        borderRadius: 12,
        padding: 20,
        shadowColor: '#000',
        shadowOffset: {
            width: 0,
            height: 2,
        },
        shadowOpacity: 0.1,
        shadowRadius: 3.84,
        elevation: 3,
    },
    quickStatsRow: {
        flexDirection: 'row',
        justifyContent: 'space-around',
        alignItems: 'center',
    },
    quickStat: {
        alignItems: 'center',
        flex: 1,
    },
    quickStatNumber: {
        fontSize: 28,
        fontWeight: 'bold',
        color: 'white',
        marginBottom: 4,
    },
    quickStatLabel: {
        fontSize: 14,
        color: 'rgba(255, 255, 255, 0.8)',
        fontWeight: '500',
    },
    fightHistoryHeader: {
        flexDirection: 'row',
        alignItems: 'center',
        justifyContent: 'space-between',
        marginBottom: 16,
    },
    fightHistoryContainer: {
        gap: 16,
    },
    fightHistoryItem: {
        backgroundColor: '#f9f9f9',
        borderRadius: 12,
        padding: 16,
        borderLeftWidth: 4,
        borderLeftColor: '#007AFF',
    },
    fightHeader: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: 8,
    },
    fightResultContainer: {
        flexDirection: 'row',
        alignItems: 'center',
    },
    fightResult: {
        fontSize: 14,
        fontWeight: 'bold',
        paddingHorizontal: 12,
        paddingVertical: 4,
        borderRadius: 12,
        backgroundColor: 'rgba(255, 255, 255, 0.8)',
        overflow: 'hidden',
    },
    fightDate: {
        fontSize: 12,
        color: '#666',
        fontWeight: '500',
    },
    eventTitle: {
        fontSize: 16,
        fontWeight: 'bold',
        color: '#333',
        marginBottom: 4,
    },
    eventLocation: {
        fontSize: 14,
        color: '#666',
        marginBottom: 12,
    },
    opponentSection: {
        marginBottom: 12,
    },
    opponentInfo: {
        flexDirection: 'row',
        alignItems: 'center',
    },
    opponentImage: {
        width: 50,
        height: 50,
        borderRadius: 25,
        backgroundColor: '#f0f0f0',
        marginRight: 12,
    },
    opponentImagePlaceholder: {
        width: 50,
        height: 50,
        borderRadius: 25,
        backgroundColor: '#007AFF',
        justifyContent: 'center',
        alignItems: 'center',
        marginRight: 12,
    },
    opponentImagePlaceholderText: {
        color: 'white',
        fontSize: 18,
        fontWeight: 'bold',
    },
    opponentDetails: {
        flex: 1,
    },
    opponentName: {
        fontSize: 16,
        fontWeight: 'bold',
        color: '#333',
        marginBottom: 2,
    },
    opponentCountry: {
        fontSize: 14,
        color: '#666',
        marginBottom: 2,
    },
    weightClass: {
        fontSize: 14,
        color: '#007AFF',
        fontWeight: '500',
    },
    fightDetails: {
        backgroundColor: 'rgba(0, 122, 255, 0.1)',
        borderRadius: 8,
        padding: 8,
    },
    fightDetailsText: {
        fontSize: 14,
        color: '#007AFF',
        fontWeight: '500',
        textAlign: 'center',
    },
    noHistoryContainer: {
        alignItems: 'center',
        paddingVertical: 20,
    },
    noHistoryText: {
        fontSize: 16,
        color: '#666',
        fontStyle: 'italic',
    },
});
