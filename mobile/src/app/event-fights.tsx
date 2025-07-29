import React, { useEffect, useState } from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity, ActivityIndicator } from 'react-native';
import { Image } from 'expo-image';
import { useLocalSearchParams, router } from 'expo-router';
import { Fight, FightResult, ResultType } from '../types/fight_types';
import { getFightResultById, getFightsByEvent } from '../lib/api/fight_api';
import { formatFighterName } from '../lib/utils/uiUtils';

export default function EventFightsScreen() {
    const [fights, setFights] = useState<Fight[]>([]);
    const [loading, setLoading] = useState(true);
    const [fightResults, setFightResults] = useState<Record<number, FightResult | null>>({});
    const [error, setError] = useState<string | null>(null);

    const { event_id } = useLocalSearchParams();

    useEffect(() => {
        fetchFights();
    }, [event_id]);

    const fetchFights = async () => {
        try {
            setLoading(true);
            setError(null);
            const fetchedFights = await getFightsByEvent(Number(event_id));
            setFights(fetchedFights);

            const resultsArray = await Promise.all(
                fetchedFights.map((fight) =>
                    getFightResultById(fight.id).catch(() => null)
                )
            );

            const resultsMap: Record<number, FightResult | null> = {};
            resultsArray.forEach((result, idx) => {
                resultsMap[fetchedFights[idx].id] = result;
            });
            setFightResults(resultsMap);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'An error occurred');
        } finally {
            setLoading(false);
        }
    };

    const handleFightPress = (fight_id: number) => {
        if (fightResults[fight_id]) {
            return;
        }

        router.push({
            pathname: '/make-prediction',
            params: {
                fight_id,
            },
        });
    };

    const renderFightCard = (fight: Fight, index: number) => {
        const fightResult = fightResults[fight.id];
        const isWin = fightResult && fightResult.result_type === ResultType.WIN;
        const isDrawOrNC = fightResult && !isWin;
        const fighter1Name = formatFighterName(fight.fighter_1_name);
        const fighter2Name = formatFighterName(fight.fighter_2_name);

        return (
            <TouchableOpacity key={index} style={styles.fightCard} onPress={() => handleFightPress(fight.id)} activeOpacity={0.8} disabled={fightResult !== null}>
                <View style={styles.fightHeader}>
                    <Text style={styles.fightWeight}>{fight.weight_class}</Text>
                </View>
                <View style={styles.fightersContainer}>
                    {/* Fighter 1 */}
                    <View style={styles.fighterSection}>
                        {fight.fighter_1_image ? (
                            <Image
                                source={{ uri: fight.fighter_1_image }}
                                style={[
                                    styles.fighterImage,
                                    isWin && fightResult.winner_id === fight.fighter_1_id && styles.winnerImage,
                                    isWin && fightResult.winner_id !== fight.fighter_1_id && styles.loserImage,
                                    isDrawOrNC && styles.drawImage
                                ]}
                                contentFit="cover"
                                contentPosition="top"
                            />
                        ) : (
                            <View style={[
                                styles.fighterImage,
                                isWin && fightResult.winner_id === fight.fighter_1_id && styles.winnerImage,
                                isWin && fightResult.winner_id !== fight.fighter_1_id && styles.loserImage,
                                isDrawOrNC && styles.drawImage
                            ]} />
                        )}
                        <View style={styles.fighterInfoRow}>
                            {fight.fighter_1_flag ? (
                                <Image
                                    source={{ uri: fight.fighter_1_flag }}
                                    style={styles.flagImage}
                                    contentFit="cover"
                                />
                            ) : null}
                            <View style={styles.fighterNameContainer}>
                                <Text style={styles.fighterFirstName}>{fighter1Name.firstName}</Text>
                                {fighter1Name.lastName !== '' && (
                                    <Text style={styles.fighterLastName}>{fighter1Name.lastName}</Text>
                                )}
                            </View>
                        </View>
                        {fight.fighter_1_ranking ? (
                            <Text style={styles.fighterRank}>{`#${fight.fighter_1_ranking}`}</Text>
                        ) : null}
                    </View>

                    {/* VS */}
                    <View style={styles.vsContainer}>
                        <Text style={styles.vsText}>VS</Text>
                    </View>

                    {/* Fighter 2 */}
                    <View style={styles.fighterSection}>
                        {fight.fighter_2_image ? (
                            <Image
                                source={{ uri: fight.fighter_2_image }}
                                style={[
                                    styles.fighterImage,
                                    isWin && fightResult.winner_id === fight.fighter_2_id && styles.winnerImage,
                                    isWin && fightResult.winner_id !== fight.fighter_2_id && styles.loserImage,
                                    isDrawOrNC && styles.drawImage
                                ]}
                                contentFit="cover"
                                contentPosition="top"
                            />
                        ) : (
                            <View style={[
                                styles.fighterImage,
                                isWin && fightResult.winner_id === fight.fighter_2_id && styles.winnerImage,
                                isWin && fightResult.winner_id !== fight.fighter_2_id && styles.loserImage,
                                isDrawOrNC && styles.drawImage
                            ]} />
                        )}
                        <View style={styles.fighterInfoRow}>
                            {fight.fighter_2_flag ? (
                                <Image
                                    source={{ uri: fight.fighter_2_flag }}
                                    style={styles.flagImage}
                                    contentFit="cover"
                                />
                            ) : null}
                            <View style={styles.fighterNameContainer}>
                                <Text style={styles.fighterFirstName}>{fighter2Name.firstName}</Text>
                                {fighter2Name.lastName !== '' && (
                                    <Text style={styles.fighterLastName}>{fighter2Name.lastName}</Text>
                                )}
                            </View>
                        </View>
                        {fight.fighter_2_ranking ? (
                            <Text style={styles.fighterRank}>{`#${fight.fighter_2_ranking}`}</Text>
                        ) : null}
                    </View>
                </View>
                {/* Fight Result */}
                {fightResult && (
                    <View style={styles.resultContainer}>
                        <Text style={styles.resultText}>{`${fightResult.method} | Round ${fightResult.round} | ${fightResult.time}`}</Text>
                    </View>
                )}
            </TouchableOpacity>
        );
    };

    return (
        <View style={styles.container}>
            {/* Header with back button */}
            <View style={styles.header}>
                <TouchableOpacity onPress={() => router.back()} style={styles.backButton}>
                    <Text style={styles.backButtonText}>← Back</Text>
                </TouchableOpacity>
                <Text style={styles.headerText}>Event Details</Text>
                <View style={styles.placeholder} />
            </View>

            <ScrollView style={styles.scrollView}>
                <View style={styles.mainContent}>
                    {/* All Fights */}
                    <Text style={styles.fightsTitle}>All Fights ({fights.length})</Text>
                    {loading ? (
                        <ActivityIndicator size="large" color="#000" style={{ marginTop: 20 }} />
                    ) : error ? (
                        <Text style={{ color: 'red', textAlign: 'center', marginTop: 20 }}>{error}</Text>
                    ) : fights.length === 0 ? (
                        <Text style={{ textAlign: 'center', marginTop: 20 }}>No fights found for this event.</Text>
                    ) : (
                        fights.slice().reverse().map((fight, index) => renderFightCard(fight, index))
                    )}
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
    scrollView: {
        flex: 1,
    },
    mainContent: {
        paddingHorizontal: 16,
        paddingTop: 20,
        paddingBottom: 20,
    },
    fightsTitle: {
        fontSize: 22,
        fontWeight: 'bold',
        marginBottom: 16,
        textAlign: 'center',
    },
    fightCard: {
        backgroundColor: 'white',
        borderRadius: 16,
        padding: 16,
        marginBottom: 16,
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 2 },
        shadowOpacity: 0.12,
        shadowRadius: 4,
        elevation: 4,
    },
    fightHeader: {
        flexDirection: 'row',
        alignItems: 'center',
        justifyContent: 'center',
        marginBottom: 12,
        paddingBottom: 6,
        borderBottomWidth: 1,
        borderBottomColor: '#eee',
    },
    fightWeight: {
        fontSize: 16,
        fontWeight: '700',
        backgroundColor: '#e0e7ef',
        color: '#2a3a4d',
        paddingHorizontal: 18,
        paddingVertical: 6,
        borderRadius: 20,
        alignSelf: 'center',
        marginVertical: 4,
        overflow: 'hidden',
    },
    fightersContainer: {
        flexDirection: 'row',
        alignItems: 'center',
        justifyContent: 'space-between',
        marginTop: 8,
    },
    fighterSection: {
        flex: 1,
        alignItems: 'center',
        justifyContent: 'center',
    },
    fighterImage: {
        width: 90,
        height: 90,
        borderRadius: 12,
        marginBottom: 8,
        backgroundColor: '#fafafa',
    },
    winnerImage: {
        borderColor: '#28A745',
        borderWidth: 3,
        shadowColor: '#28A745',
        shadowOffset: { width: 0, height: 2 },
        shadowOpacity: 0.3,
        shadowRadius: 6,
        elevation: 6,
    },
    drawImage: {
        borderColor: '#999',
        borderWidth: 3,
        shadowColor: '#999',
        shadowOffset: { width: 0, height: 2 },
        shadowOpacity: 0.3,
        shadowRadius: 6,
        elevation: 6,
    },
    loserImage: {
        borderColor: '#FF3B30', // system red shade
        borderWidth: 3,
        shadowColor: '#FF3B30',
        shadowOffset: { width: 0, height: 2 },
        shadowOpacity: 0.3,
        shadowRadius: 6,
        elevation: 6,
    },
    fighterInfoRow: {
        flexDirection: 'row',
        alignItems: 'center',
        marginBottom: 2,
    },
    flagImage: {
        width: 32,
        height: 24,
        marginRight: 6,
        borderRadius: 4,
        overflow: 'hidden',
        backgroundColor: '#fff',
        alignSelf: 'center',
    },
    fighterNameContainer: {
        alignItems: 'flex-start',
        justifyContent: 'center',
    },
    fighterFirstName: {
        fontSize: 15,
        fontWeight: 'bold',
        textAlign: 'left',
        color: '#222',
    },
    fighterLastName: {
        fontSize: 15,
        fontWeight: 'bold',
        textAlign: 'left',
        color: '#222',
        marginTop: 1,
    },
    fighterRank: {
        fontSize: 12,
        color: '#888',
        marginTop: 2,
        fontWeight: '600',
    },
    vsContainer: {
        width: 48,
        alignItems: 'center',
        justifyContent: 'center',
    },
    vsText: {
        fontSize: 20,
        fontWeight: 'bold',
        color: '#666',
    },
    resultContainer: {
        marginTop: 12,
        alignItems: 'center',
        paddingTop: 6,
        borderTopWidth: 1,
        borderTopColor: '#eee',
    },
    resultText: {
        fontSize: 14,
        fontWeight: '600',
        color: '#444',
    },
    eventDate: {
        fontSize: 14,
        color: '#666',
        marginBottom: 8,
    },
    eventVenue: {
        fontSize: 14,
        color: '#666',
    },
}); 