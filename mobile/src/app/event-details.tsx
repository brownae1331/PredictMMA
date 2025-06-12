import React, { useEffect, useState } from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity, ActivityIndicator } from 'react-native';
import { Image } from 'expo-image';
import { useLocalSearchParams, router } from 'expo-router';
import { Event, Fight } from '../types/ufc_types';
import { getEventFights } from '../lib/api';

export default function EventDetailsScreen() {
    const { eventData } = useLocalSearchParams();
    const event: Event = JSON.parse(eventData as string);
    const [fights, setFights] = useState<Fight[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchFights = async () => {
            try {
                setLoading(true);
                setError(null);
                const data = await getEventFights(event.event_url);
                setFights(data);
            } catch (err) {
                setError(err instanceof Error ? err.message : 'An error occurred');
            } finally {
                setLoading(false);
            }
        };
        fetchFights();
    }, [event.event_url]);

    const formatFighterName = (fullName: string) => {
        const nameParts = fullName.trim().split(' ');
        if (nameParts.length === 1) {
            return { firstName: nameParts[0], lastName: '' };
        }
        const firstName = nameParts[0];
        const lastName = nameParts.slice(1).join(' ');
        return { firstName, lastName };
    };

    const renderFightCard = (fight: Fight, index: number) => {
        const fighter1Name = formatFighterName(fight.fighter_1_name);
        const fighter2Name = formatFighterName(fight.fighter_2_name);

        return (
            <View key={index} style={styles.fightCard}>
                <View style={styles.fightHeader}>
                    <View style={styles.centerSection}>
                        <Text style={styles.fightWeight}>{fight.fight_weight}</Text>
                    </View>
                </View>
                <View style={styles.fightersContainer}>
                    <View style={styles.fighter}>
                        <Image
                            source={{ uri: fight.fighter_1_image }}
                            style={styles.fighterImage}
                            contentFit="cover"
                            contentPosition="top"
                        />
                        <View style={styles.fighterNameContainer}>
                            <Text style={styles.fighterFirstName}>{fighter1Name.firstName}</Text>
                            {fighter1Name.lastName !== '' && (
                                <Text style={styles.fighterLastName}>{fighter1Name.lastName}</Text>
                            )}
                        </View>
                    </View>
                    <Text style={styles.vsText}>VS</Text>
                    <View style={styles.fighter}>
                        <Image
                            source={{ uri: fight.fighter_2_image }}
                            style={styles.fighterImage}
                            contentFit="cover"
                            contentPosition="top"
                        />
                        <View style={styles.fighterNameContainer}>
                            <Text style={styles.fighterFirstName}>{fighter2Name.firstName}</Text>
                            {fighter2Name.lastName !== '' && (
                                <Text style={styles.fighterLastName}>{fighter2Name.lastName}</Text>
                            )}
                        </View>
                    </View>
                </View>
            </View>
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
                        fights.map((fight, index) => renderFightCard(fight, index))
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
        borderRadius: 12,
        padding: 12,
        marginBottom: 12,
        shadowColor: '#000',
        shadowOffset: {
            width: 0,
            height: 2,
        },
        shadowOpacity: 0.1,
        shadowRadius: 3.84,
        elevation: 3,
    },
    fightHeader: {
        flexDirection: 'row',
        alignItems: 'center',
        marginBottom: 12,
        paddingBottom: 6,
        borderBottomWidth: 1,
        borderBottomColor: '#eee',
    },
    centerSection: {
        flex: 1,
        alignItems: 'center',
    },
    fightWeight: {
        fontSize: 12,
        fontWeight: '600',
        backgroundColor: '#FFD700',
        paddingHorizontal: 8,
        paddingVertical: 2,
        borderRadius: 4,
    },
    fightersContainer: {
        flexDirection: 'row',
        alignItems: 'center',
        justifyContent: 'space-between',
    },
    fighter: {
        flex: 1,
        alignItems: 'center',
    },
    fighterImage: {
        width: 90,
        height: 90,
        borderRadius: 12,
        marginBottom: 8,
    },
    fighterNameContainer: {
        alignItems: 'center',
        minHeight: 35,
        justifyContent: 'center',
    },
    fighterFirstName: {
        fontSize: 13,
        fontWeight: 'bold',
        textAlign: 'center',
        paddingHorizontal: 4,
    },
    fighterLastName: {
        fontSize: 13,
        fontWeight: 'bold',
        textAlign: 'center',
        paddingHorizontal: 4,
        marginTop: 2,
    },
    vsText: {
        fontSize: 18,
        fontWeight: 'bold',
        color: '#666',
        marginHorizontal: 12,
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